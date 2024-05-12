FROM ubuntu:16.04

RUN apt-get update && apt-get install -y \
	curl \
	python2.7 \
&& rm -rf /var/lib/apt/lists/*



COPY . /packman

WORKDIR /packman

CMD ["python2", "pacman.py", "-p", "ApproximateQAgent", "-a", "extractor=SimpleExtractor", "-x", "50", "-n", "60", "-l", "trickyClassic"]