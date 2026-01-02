# MiniDB Docker Setup

This Docker setup allows you to run the MiniDB application (server.py + gui.py) automatically without manually executing commands. When you start the container, it will automatically start the server first, wait for it to be ready, and then launch the GUI.

## Prerequisites

- Docker Engine (20.10+)
- Docker Compose (v2.0+)
- X11 display server (for GUI support)

## Quick Start

### 1. Build and Run with Docker Compose

```bash
# Build the Docker image
docker-compose build

# Run the application
docker-compose up
```

### 2. Run with Docker Commands

```bash
# Build the image
docker build -t minimdb .

# Run with X11 forwarding
docker run -it --rm \
    -e DISPLAY=${DISPLAY} \
    -v /tmp/.X11-unix:/tmp/.X11-unix:ro \
    -v $(pwd)/data:/app/data \
    minimdb
```

## Project Structure

```
DATABASE-IN-CPP/
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose configuration
├── entrypoint.sh           # Startup script (runs server.py → gui.py)
├── requirements.txt        # Python dependencies
├── minmax/
│   ├── server.py          # Flask API server (runs first)
│   └── gui.py             # Tkinter GUI (runs after server)
└── ...
```

## How It Works

The Docker setup uses a smart entrypoint script that:

1. **Starts server.py**: Launches the Flask API server in the background on port 8080
2. **Waits for readiness**: Continuously checks if the server is ready (up to 30 seconds)
3. **Starts gui.py**: Once server is ready, launches the Tkinter GUI application
4. **Cleanup**: When GUI exits, automatically stops the server

### Startup Sequence

```
Container starts
    ↓
entrypoint.sh executed
    ↓
server.py starts in background (PID saved)
    ↓
Wait for server to respond at http://localhost:8080/api/health
    ↓
Server ready → Launch gui.py
    ↓
GUI displays application window
    ↓
User works with MiniDB
    ↓
User closes GUI → Server automatically stopped
```

## GUI Display (X11 Forwarding)

Since this application includes a graphical interface, you need to configure X11 forwarding to display the GUI from the container.

### Linux

X11 forwarding typically works out of the box on Linux:

```bash
# Check your DISPLAY variable
echo $DISPLAY
# Usually returns something like ":0"

# Ensure X11 socket permissions
xhost +local:docker
```

### macOS

For macOS, use XQuartz:

1. Install XQuartz: `brew install --cask xquartz`
2. Restart XQuartz and enable "Allow connections from network clients"
3. Set DISPLAY variable:

```bash
# Get your IP address
ifconfig en0 | grep inet | awk '$1=="inet" {print $2}'

# Run container with your IP
docker run -it --rm \
    -e DISPLAY=192.168.x.x:0 \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    minimdb
```

### Windows

For Windows with WSL2:

1. Install VcXsrv or Xming
2. Configure WSL to use the Windows X server
3. Set DISPLAY variable in WSL:

```bash
# Add to ~/.bashrc or ~/.zshrc
export DISPLAY=$(grep nameserver /etc/resolv.conf | awk '{print $2}'):0
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DISPLAY | :0 | X11 display server address |
| PYTHONDONTWRITEBYTECODE | 1 | Prevent .pyc files creation |
| PYTHONUNBUFFERED | 1 | Real-time Python output |

### Port Configuration

The server runs on port 8080. You can modify this in `docker-compose.yml`:

```yaml
services:
  database-app:
    ports:
      - "custom_port:8080"  # e.g., "9090:8080"
```

## Managing the Container

### View Logs

```bash
# All logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# Container-specific logs
docker logs minimdb
```

### Stop the Application

```bash
# Ctrl+C in terminal (if running docker-compose up)
docker-compose down

# Or stop specific container
docker stop minimdb
```

### Restart

```bash
docker-compose restart
```

## Data Persistence

By default, data is stored in-memory within the container. For persistence:

### Using Docker Volumes

```yaml
# docker-compose.yml
services:
  database-app:
    volumes:
      - ./data:/app/data
      - minimdb_data:/app/internal_data

volumes:
  minimdb_data:
```

### Backup Data

```bash
# Copy data from container
docker cp minimdb:/app/data ./backup
```

## Troubleshooting

### GUI Not Displaying

1. **Check DISPLAY variable**: Ensure it's set correctly
2. **X11 permissions**: Run `xhost +local:docker`
3. **Container display**: Verify environment variable is passed

```bash
# Debug: Check if DISPLAY is set in container
docker run --rm -it minimdb env | grep DISPLAY
```

### Server Not Starting

```bash
# Check server logs
docker logs minimdb
cat /tmp/server.log  # Inside container
```

### Port Already in Use

```bash
# Find process using port 8080
lsof -i :8080

# Kill the process or change port in docker-compose.yml
```

### Connection Refused Errors

```bash
# Verify server is running
docker exec minimdb ps aux | grep python

# Check server health endpoint
curl http://localhost:8080/api/health
```

## Advanced Usage

### Run Server Only (No GUI)

```bash
# Run only the server
docker run -it --rm -p 8080:8080 minimdb python server.py
```

### Run GUI Only (External Server)

```bash
# Connect to external server
docker run -it --rm \
    -e SERVER_URL=http://your-server-ip:8080 \
    minimdb python gui.py
```

### Development Mode

For development with hot-reloading:

```yaml
# docker-compose.dev.yml
services:
  database-app:
    build: .
    volumes:
      - ./minmax:/app/minmax
      - ./requirements.txt:/app/requirements.txt
    command: >
      bash -c "pip install -r requirements.txt -q && 
               python server.py &
               python gui.py"
```

## Security Considerations

- The container runs with full network access
- No authentication on API endpoints by default
- For production, add authentication and HTTPS
- Consider running as non-root user:

```dockerfile
# Add to Dockerfile before COPY
RUN useradd -m appuser
USER appuser
```

## System Requirements

- **RAM**: Minimum 512MB, Recommended 1GB
- **CPU**: x86_64 or ARM64 architecture
- **Storage**: ~200MB for Docker image

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Support

For issues with:
- **Docker**: Check [Docker Documentation](https://docs.docker.com/)
- **X11 Forwarding**: See your OS-specific X11 documentation
- **Application**: Open an issue on the [GitHub repository](https://github.com/maisum77/DATABASE-IN-CPP.git)
