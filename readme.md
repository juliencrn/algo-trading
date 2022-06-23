# Algo Trading

Discover both data analysis and algorithmic trading strategies

## Install

To access to the Jupyter Lab from your Browser, you need a RSA Key. You can generate one using this command:

```sh
# Generate RSA keys to secure web services (used for Jupyter)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout .jupyter/mykey.key -out .jupyter/mycert.pem

# Generate github SSH key
ssh-keygen -t ed25519 -C "your_email@example.com" <path/to/repo>/gh

```

Then install the dependencies: 
- On a server using Ubuntu (like a DigitalOcean droplet)
- Using Docker (Explained below)

### Getting started using Docker

```sh
# build the image
docker build -t jupyterlab .

# run the container
docker run -it --rm -p 8888:8888 jupyterlab 
```
