extern "C" {
#include <libxlnk_cma.h>
}
#include <linux/vfio.h>
#include <unistd.h>
#include <libgen.h>
#include <map>
#include <iostream>
#include <string>

#define DEVICE_NAME "80000000.fabric-vfio"
#define PATH_LENGTH 260

static unsigned long const PAGE_MASK = (1 << 12) - 1;

int container_fd;
int group_fd;
int device_fd;

uint64_t region_offset;
uint32_t next_alloc = 0x1000;

std::map<void*, std::pair<unsigned long, uint32_t> > alloc_map;


__attribute__((constructor (1000)))
static void init_fds(void) {
	std::string iommu_link = std::string("/sys/bus/platform/devices/") +
		std::string(DEVICE_NAME) + "/iommu_group";
	char buf[PATH_LENGTH];
	ssize_t ret = readlink(iommu_link.c_str(), buf, PATH_LENGTH);
	if (ret == -1) {
		std::cerr << "Failed to read iommu_group link: " << ret << std::endl;
		return;
	}
	int group_num = atoi(basename(buf));
	snprintf(buf, PATH_LENGTH, "/dev/vfio/%d", group_num);
	container_fd = open("/dev/vfio/vfio", O_RDWR);
	if (container_fd < 0) {
		std::cerr << "Failed to open container: " << container_fd << std::endl;
		return;
	}
	group_fd = open(buf, O_RDWR);
	if (group_fd < 0) {
		std::cerr << "Failed to open group " << buf << ": " << group_fd << std::endl;
		return;
	}
	ret = ioctl(group_fd, VFIO_GROUP_SET_CONTAINER, &container_fd);
	if (ret) {
		std::cerr << "Failed to set container: " << ret <<std::endl;
		return;
	}
	ret = ioctl(container_fd, VFIO_SET_IOMMU, VFIO_TYPE1_IOMMU);
	device_fd = ioctl(group_fd, VFIO_GROUP_GET_DEVICE_FD, DEVICE_NAME);
	if (device_fd < 0) {
		std::cerr << "Failed to create device: " << device_fd << std::endl;
		return;
	}
	vfio_region_info region_info;
	region_info.argsz = sizeof(region_info);
	region_info.flags = 0;
	region_info.index = 0;
	region_info.cap_offset = 0;
	region_info.size = 0;
	region_info.offset = 0;

	ret = ioctl(device_fd, VFIO_DEVICE_GET_REGION_INFO, &region_info);
	region_offset = region_info.offset;
}

unsigned long cma_mmap(unsigned long phyAddr, uint32_t len) {
	if (phyAddr < 0x80000000 || (phyAddr + len) > 0xC0000000) {
		return 0;
	}
	unsigned long mmap_offset = phyAddr - 0x80000000 + region_offset;
	// Make sure we are 4K aligned
	unsigned long page_offset = mmap_offset & PAGE_MASK;
	unsigned long page_base = mmap_offset & ~PAGE_MASK;
	len = ((len + page_offset - 1) | PAGE_MASK) + 1;
	void* mapped_base = mmap(NULL, len, PROT_READ | PROT_WRITE, MAP_SHARED, device_fd, page_base);
	if (mapped_base == MAP_FAILED) return (unsigned long)MAP_FAILED;
	return (unsigned long)mapped_base + page_offset;

}

uint32_t cma_munmap(void* buf, uint32_t len) {
	unsigned long mmap_offset = (unsigned long)buf;	
	unsigned long page_offset = mmap_offset & PAGE_MASK;
	unsigned long page_base = mmap_offset & ~PAGE_MASK;
	len = ((len + page_offset - 1) | PAGE_MASK) + 1;
	munmap((void*)page_base, len);
	return 0;
}

void* cma_alloc(uint32_t len, uint32_t cacheable) {
	len = ((len - 1) | PAGE_MASK) + 1;
	void* virtaddr = mmap(NULL, len, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, 0, 0);
	if (virtaddr == MAP_FAILED) return 0;
	vfio_iommu_type1_dma_map mapcmd;
	mapcmd.argsz = sizeof(mapcmd);
	mapcmd.vaddr = (intptr_t)virtaddr;
	mapcmd.iova = next_alloc;
	mapcmd.size = len;
	mapcmd.flags = VFIO_DMA_MAP_FLAG_READ | VFIO_DMA_MAP_FLAG_WRITE;
	int ret = ioctl(container_fd, VFIO_IOMMU_MAP_DMA, &mapcmd);
	if (ret) {
		munmap(virtaddr, len);
		return 0;
	}
	alloc_map[virtaddr] = std::make_pair(next_alloc, len);
	next_alloc += len;
	return virtaddr;

}

unsigned long cma_get_phy_addr(void* buf) {
	return alloc_map[buf].first;
}

void cma_free(void* buf) {
	auto iter = alloc_map.find(buf);
	if (iter == alloc_map.end()) {
		return;
	}
	vfio_iommu_type1_dma_unmap mapcmd;
	mapcmd.argsz = sizeof(mapcmd);
	mapcmd.size = iter->second.second;
	mapcmd.iova = iter->second.first;
	int ret = ioctl(container_fd, VFIO_IOMMU_UNMAP_DMA, &mapcmd);
	if (ret) {
		return;
	}
	alloc_map.erase(iter);
	munmap(buf, iter->second.second);
}

uint32_t cma_pages_available() {
	return 0;
}

void cma_flush_cache(void* buf, unsigned int phys_addr, int size) {
    uintptr_t begin = (uintptr_t)buf;
    uintptr_t line = begin &~0x3FULL;
    uintptr_t end = begin + size;

    uintptr_t stride = 64; // TODO: Make this architecture dependent

    asm volatile(
    "loop:\n\t"
    "dc civac, %[line]\n\t"
    "add %[line], %[line], %[stride]\n\t"
    "cmp %[line], %[end]\n\t"
    "b.lt loop\n\t"
    ::[line] "r" (line),
    [stride] "r" (stride),
    [end] "r" (end)
    : "cc", "memory"
    );
}

void cma_invalidate_cache(void* buf, unsigned int phys_addr, int size) {
	cma_flush_cache(buf, phys_addr, size);
}
