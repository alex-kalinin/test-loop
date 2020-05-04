FROM guyroyse/redismod
# FROM redislabs/redisedge:latest

ENV DEPS "python python3-pip python3-setuptools libglib2.0-0 libsm6 libxrender1 libxext6 libgomp1"
RUN set -ex; \
    apt-get update; \
    apt-get install -y --no-install-recommends $DEPS;

RUN set -ex ;\
	apt-get install -y wget python3-distutils ;\
	wget -q https://bootstrap.pypa.io/get-pip.py -O /tmp/get-pip.py ;\
	python3 /tmp/get-pip.py;

RUN set -ex; \
    pip3 install -U pipenv;

RUN set -ex; \
    cd /opt/redislabs/lib/modules/python3; \
    pipenv run pip3 install imageio python-twitter pillow opencv-python

CMD ["--loadmodule /usr/lib/redis/modules/redisai.so", "--loadmodule /usr/lib/redis/modules/redistimeseries.so", "--loadmodule /opt/redislabs/lib/modules/redisgears.so PythonHomeDir /opt/redislabs/lib/modules/python3"]

