FROM rockylinux:9.1.20230215

# Install packages
RUN dnf install -y wget tar openssh-clients python3.12 python3-pip && dnf clean all

RUN mkdir /app

# Setup OpenMPI
COPY openmpi-4.0.0 /app/openmpi-4.0.0
RUN ln -s /app/openmpi-4.0.0 /app/openmpi

ENV PATH="/app/openmpi/bin:${PATH}"
ENV LD_LIBRARY_PATH="/app/openmpi/lib"
ENV OPAL_PREFIX="/app/openmpi"

# Setup HPS_ST3D
COPY HPS_ST3D /app/HPS_ST3D

ENV PATH="/app/HPS_ST3D/bin:${PATH}"

# Setup FastAPI application
COPY src /app/code
WORKDIR /app/code

RUN python -m venv venv
RUN source venv/bin/activate
RUN pip install -e .

ENV HPS_ST3D_EXEC="/app/HPS_ST3D/bin/HPS_ST3D"
ENV PYTHONPATH=/app/code/src


CMD ["uvicorn", "src.app:main", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000", "--no-server-header"]
