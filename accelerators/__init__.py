from accelerators.cpu import CPUAccelerator
from accelerators.cuda import CUDAAccelerator
from accelerators.opencl import OpenCLAccelerator

def get_available_accelerators():
    accs = [CPUAccelerator()]
    cuda = CUDAAccelerator()
    if cuda.is_available():
        accs.append(cuda)
    opencl = OpenCLAccelerator()
    if opencl.is_available():
        accs.append(opencl)
    return accs
