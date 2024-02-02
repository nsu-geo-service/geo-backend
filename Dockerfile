FROM python:3.12-bookworm

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
COPY . /app/code
WORKDIR /app/code

RUN python -m venv venv
RUN . venv/bin/activate
RUN pip install -e .

ENV DEBUG=0
ENV FDSN_BASE="http://84.237.52.214:8080"
ENV HPS_ST3D_EXEC="/app/HPS_ST3D/bin/HPS_ST3D"

ENV PYTHONPATH=/app/code/src

CMD ["uvicorn", "src.geo.main:application", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000", "--no-server-header"]
