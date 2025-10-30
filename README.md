# Beasiswa Indonesia Monitoring Dashboard

A comprehensive data engineering project for monitoring and tracking Master's and PhD scholarship opportunities for Indonesian students. Built with Apache Airflow for data orchestration, Docker for containerization, and Streamlit for interactive visualization.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Data Pipeline](#data-pipeline)
- [Dashboard Features](#dashboard-features)
- [Troubleshooting](#troubleshooting)
- [Maintenance](#maintenance)
- [Contributing](#contributing)
- [License](#license)

## Overview

This project provides an automated system for tracking scholarship opportunities across multiple countries and institutions. The system uses Apache Airflow to orchestrate daily data collection and processing tasks, storing results in a shared data layer that powers a real-time Streamlit dashboard.

### Key Components

- **Apache Airflow**: Orchestrates ETL pipelines for data collection and processing
- **PostgreSQL**: Stores Airflow metadata and task execution history
- **Streamlit**: Provides interactive web-based dashboard for data visualization
- **Docker**: Ensures consistent deployment across different environments

## Features

- **Automated Data Collection**: Daily scheduled pipeline to collect scholarship information
- **Real-time Status Tracking**: Monitors which scholarships are currently open, upcoming, or closed
- **Interactive Visualization**: Timeline-based Gantt charts for easy deadline tracking
- **Advanced Filtering**: Filter scholarships by degree level, country, and status
- **Responsive Design**: Mobile-friendly interface with modern UI/UX
- **Extensible Architecture**: Easy to add new data sources and visualization components

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Compose                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │              │  │              │  │              │       │
│  │  PostgreSQL  │  │   Airflow    │  │  Streamlit   │       │
│  │   Database   │◄─┤  Webserver   │  │  Dashboard   │       │
│  │              │  │              │  │              │       │
│  └──────────────┘  └──────────────┘  └──────┬───────┘       │
│         ▲                  ▲                  │             │
│         │                  │                  │             │
│         │          ┌───────┴────────┐         │             │
│         │          │                │         │             │
│         └──────────┤    Airflow     │         │             │
│                    │   Scheduler    │         │             │
│                    │                │         │             │
│                    └────────┬───────┘         │             │
│                             │                 │             │
│                             ▼                 ▼             │
│                    ┌─────────────────────────────┐          │
│                    │    Shared Data Volume       │          │
│                    │  - beasiswa.csv             │          │
│                    │  - beasiswa_processed.csv   │          │
│                    │  - stats.json               │          │
│                    └─────────────────────────────┘          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Docker** (version 20.10 or higher)
  ```bash
  docker --version
  ```

- **Docker Compose** (version 1.29 or higher)
  ```bash
  docker-compose --version
  ```

- **Minimum System Requirements**:
  - RAM: 4GB (8GB recommended)
  - Disk Space: 10GB free space
  - OS: Linux, macOS, or Windows 10/11 with WSL2

## Installation

### Step 1: Create Project Directory Structure

Clone the main project:

```bash
mkdir -p beasiswa-dashboard/{airflow,streamlit,dags,data,logs}
cd beasiswa-dashboard
```

### Step 2: Create Configuration Files

#### 2.1 Docker Compose Configuration

Create `docker-compose.yml` in the root directory:

```bash
touch docker-compose.yml
```

Copy the content from the artifact **"Docker Compose - Beasiswa Dashboard"** into this file.

#### 2.2 Airflow Configuration

Create Airflow Dockerfile:

```bash
touch airflow/Dockerfile
```

Copy the content from the artifact **"Dockerfile - Airflow"** into this file.

Create Airflow initialization script:

```bash
touch airflow/init_airflow.sh
```

Copy the content from the artifact **"init_airflow.sh - Airflow Initialization"** into this file.

Set executable permission for the initialization script:

```bash
chmod +x airflow/init_airflow.sh
```

#### 2.3 Streamlit Configuration

Create Streamlit Dockerfile:

```bash
touch streamlit/Dockerfile
```

Copy the content from the artifact **"Dockerfile - Streamlit"** into this file.

Create Streamlit application:

```bash
touch streamlit/app.py
```

Copy the content from the artifact **"Streamlit Dashboard App"** into this file.

#### 2.4 Airflow DAG

Create the data pipeline DAG:

```bash
touch dags/beasiswa_dag.py
```

Copy the content from the artifact **"DAG - Scrape Beasiswa"** into this file.

### Step 3: Verify Project Structure

Verify your directory structure matches the following:

```
beasiswa-dashboard/
├── docker-compose.yml
├── airflow/
│   ├── Dockerfile
│   └── init_airflow.sh
├── streamlit/
│   ├── Dockerfile
│   └── app.py
├── dags/
│   └── beasiswa_dag.py
├── data/
└── logs/
```

You can verify this using:

```bash
tree -L 2
# or
find . -type f -o -type d | sort
```

### Step 4: Build Docker Images

Build all required Docker images:

```bash
docker-compose build
```

This process may take 5-10 minutes depending on your internet connection and system performance.

### Step 5: Start All Services

Launch all services in detached mode:

```bash
docker-compose up -d
```

### Step 6: Verify Services are Running

Check the status of all containers:

```bash
docker-compose ps
```

Expected output should show all services as "Up" or "healthy":

```
NAME                    STATUS              PORTS
postgres                Up                  5432/tcp
airflow-webserver       Up                  0.0.0.0:8080->8080/tcp
airflow-scheduler       Up
streamlit               Up                  0.0.0.0:8501->8501/tcp
```

Monitor logs to ensure services start correctly:

```bash
docker-compose logs -f
```

Press `Ctrl+C` to stop viewing logs.

## Configuration

### Airflow Configuration

Access Apache Airflow web interface:

- **URL**: http://localhost:8080
- **Username**: `admin`
- **Password**: `admin`

### Default Settings

The following default configurations are set:

- **Airflow Executor**: LocalExecutor
- **DAG Schedule**: Daily at midnight (00:00)
- **Data Directory**: `./data/` (shared volume)
- **Timezone**: System default (adjust in DAG if needed)

### Modifying Schedule

To change the pipeline execution schedule, edit `dags/beasiswa_dag.py`:

```python
dag = DAG(
    'beasiswa_scraper',
    schedule_interval='0 0 * * *',  # Modify this cron expression
    ...
)
```

Common schedule patterns:

- `'0 0 * * *'` - Daily at midnight
- `'0 */6 * * *'` - Every 6 hours
- `'0 0 * * 1'` - Every Monday
- `'@hourly'` - Every hour
- `'@daily'` - Once per day

## Usage

### Accessing the Dashboard

Open your web browser and navigate to:

```
http://localhost:8501
```

### Running the Data Pipeline

#### Method 1: Automatic Execution (Scheduled)

The pipeline runs automatically every day at midnight. No manual intervention required.

#### Method 2: Manual Execution

1. Navigate to Airflow UI: http://localhost:8080
2. Login with credentials (`admin` / `admin`)
3. Locate the DAG named `beasiswa_scraper`
4. Toggle the DAG to "On" state using the switch on the left
5. Click the "Play" button (▶) to trigger a manual run
6. Monitor execution in the Grid or Graph view
7. Once completed (status shows green), refresh the Streamlit dashboard

### Viewing Pipeline Logs

#### Via Airflow UI

1. Go to Airflow UI
2. Click on the DAG `beasiswa_scraper`
3. Select the task instance
4. Click "Log" to view detailed execution logs

#### Via Command Line

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs airflow-scheduler
docker-compose logs airflow-webserver
docker-compose logs streamlit

# Follow logs in real-time
docker-compose logs -f airflow-scheduler
```

## Project Structure

### Directory Layout

```
beasiswa-dashboard/
│
├── docker-compose.yml              # Docker orchestration configuration
│
├── airflow/                        # Airflow container configuration
│   ├── Dockerfile                  # Airflow image specification
│   └── init_airflow.sh            # Database initialization script
│
├── streamlit/                      # Streamlit application
│   ├── Dockerfile                  # Streamlit image specification
│   └── app.py                      # Main dashboard application
│
├── dags/                          # Airflow DAGs directory
│   └── beasiswa_dag.py            # Data pipeline definition
│
├── data/                          # Shared data storage (auto-generated)
│   ├── beasiswa.csv               # Raw scholarship data
│   ├── beasiswa_processed.csv     # Processed data with status
│   └── stats.json                 # Summary statistics
│
└── logs/                          # Airflow execution logs
    └── scheduler/                 # Scheduler logs
```

### Key Files Description

**docker-compose.yml**
- Defines all services (PostgreSQL, Airflow, Streamlit)
- Configures networking and volume mounts
- Sets environment variables

**dags/beasiswa_dag.py**
- Defines the ETL pipeline
- Contains scraping and processing logic
- Scheduled execution configuration

**streamlit/app.py**
- Dashboard UI implementation
- Data visualization components
- User interaction logic

## Data Pipeline

### Pipeline Stages

#### Stage 1: Data Collection (`scrape_beasiswa`)

Collects scholarship information from various sources:

- Scholarship name and institution
- Degree level (Master/PhD)
- Country/region
- Application opening date
- Application closing date
- Program description
- Official website URL

**Duration**: ~2-5 minutes (depends on data sources)

#### Stage 2: Data Processing (`process_timeline`)

Processes raw data and calculates:

- Current status (Open, Upcoming, Closed)
- Days remaining until deadline
- Days until opening (for upcoming scholarships)
- Summary statistics

**Duration**: ~30 seconds

### Data Flow

```
┌─────────────┐
│   Scraping  │
│    Source   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Extract & Parse │
│  (Task 1)       │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Store Raw Data │
│  beasiswa.csv   │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Process & Enrich│
│    (Task 2)     │
└──────┬──────────┘
       │
       ▼
┌─────────────────────────────┐
│    Store Processed Data     │
│ - beasiswa_processed.csv    │
│ - stats.json                │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────┐
│   Streamlit     │
│   Dashboard     │
└─────────────────┘
```

### Output Files

**beasiswa.csv**
```csv
nama,jenjang,negara,buka,tutup,url,deskripsi
LPDP BPI,Master/PhD,Worldwide,2024-03-01,2024-04-30,https://...,Full scholarship...
```

**beasiswa_processed.csv**
```csv
nama,jenjang,negara,buka,tutup,url,deskripsi,status,hari_tersisa
LPDP BPI,Master/PhD,Worldwide,2024-03-01,2024-04-30,https://...,Full...,Sedang Buka (15 hari lagi),15
```

**stats.json**
```json
{
  "total_beasiswa": 10,
  "sedang_buka": 3,
  "akan_buka": 4,
  "sudah_tutup": 3,
  "last_update": "2024-10-30T08:00:00"
}
```

## Dashboard Features

### Overview Section

- **Total Scholarships**: Count of all tracked scholarships
- **Currently Open**: Scholarships accepting applications
- **Opening Soon**: Upcoming opportunities
- **Closed**: Historical data

### Timeline Visualization

Interactive Gantt chart displaying:
- Scholarship application periods
- Current date marker
- Color-coded status (Green: Open, Yellow: Upcoming, Red: Closed)
- Hover information with full details

### Filtering Options

**By Degree Level**:
- Master's programs
- PhD programs
- Combined Master/PhD

**By Country/Region**:
- Multi-select dropdown
- Includes all available countries

**By Status**:
- Show all scholarships
- Currently open only
- Opening soon only
- Closed only

### Detailed Views

**Currently Open Tab**:
- Sorted by deadline urgency
- Shows remaining days
- Direct links to application portals
- Full scholarship descriptions

**Opening Soon Tab**:
- Sorted by opening date
- Days until application opens
- Preparation timeline
- Notification options

**All Scholarships Tab**:
- Comprehensive table view
- Sortable columns
- Export capabilities
- Search functionality

## Troubleshooting

### Common Issues

#### Issue: Containers fail to start

**Symptoms**:
```bash
docker-compose ps
# Shows services as "Exit 1" or "Restarting"
```

**Solution**:
```bash
# Check logs for error messages
docker-compose logs

# Reset and rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

#### Issue: Airflow shows "Database not ready"

**Symptoms**: Airflow webserver fails to start, logs show database connection errors

**Solution**:
```bash
# Wait for PostgreSQL to fully initialize (30-60 seconds)
docker-compose logs postgres

# If still failing, recreate database
docker-compose down -v
docker-compose up -d postgres
# Wait 30 seconds
docker-compose up -d
```

#### Issue: Dashboard shows "No data available"

**Symptoms**: Streamlit loads but displays no scholarship information

**Solution**:
```bash
# Verify data files exist
docker-compose exec streamlit ls -la /app/data/

# If empty, trigger Airflow DAG manually
# Go to http://localhost:8080 and run beasiswa_scraper

# Check DAG execution logs
docker-compose logs airflow-scheduler
```

#### Issue: Port already in use

**Symptoms**:
```
Error: bind: address already in use
```

**Solution**:
```bash
# Find process using the port
lsof -i :8080  # For Airflow
lsof -i :8501  # For Streamlit

# Kill the process or change ports in docker-compose.yml
# Edit docker-compose.yml and change port mapping:
# ports:
#   - "8081:8080"  # Instead of 8080:8080
```

#### Issue: Permission denied on init_airflow.sh

**Symptoms**: Container fails to start, logs show permission error

**Solution**:
```bash
chmod +x airflow/init_airflow.sh
docker-compose down
docker-compose up -d
```

### Checking Service Health

```bash
# Overall status
docker-compose ps

# Resource usage
docker stats

# Service-specific health check
docker-compose exec airflow-webserver airflow db check
docker-compose exec postgres pg_isready -U airflow
```

### Logs and Debugging

```bash
# View all logs
docker-compose logs

# View specific service
docker-compose logs -f streamlit

# Last 100 lines
docker-compose logs --tail=100

# Save logs to file
docker-compose logs > debug.log 2>&1
```

## Maintenance

### Regular Maintenance Tasks

#### Daily
- Monitor DAG execution status
- Check dashboard accessibility

#### Weekly
- Review error logs
- Verify data accuracy
- Check disk space usage

#### Monthly
- Update scholarship data sources
- Review and optimize DAG performance
- Backup data files

### Backup and Restore

#### Backup Data

```bash
# Create backup directory
mkdir -p backups/$(date +%Y%m%d)

# Backup data files
cp -r data/* backups/$(date +%Y%m%d)/

# Backup Airflow database
docker-compose exec postgres pg_dump -U airflow airflow > backups/$(date +%Y%m%d)/airflow_db.sql
```

#### Restore Data

```bash
# Restore data files
cp -r backups/YYYYMMDD/* data/

# Restore Airflow database
docker-compose exec -T postgres psql -U airflow airflow < backups/YYYYMMDD/airflow_db.sql
```

### Updating the Application

```bash
# Pull latest changes (if using version control)
git pull

# Rebuild containers
docker-compose build

# Restart services
docker-compose down
docker-compose up -d
```

### Clearing Old Data

```bash
# Remove processed data (will be regenerated)
rm -f data/beasiswa_processed.csv data/stats.json

# Clear Airflow logs older than 30 days
find logs/ -name "*.log" -mtime +30 -delete

# Trigger new pipeline run
# Go to Airflow UI and trigger beasiswa_scraper DAG
```

## Stopping and Removing Services

### Stop Services (Preserve Data)

```bash
docker-compose stop
```

### Start Stopped Services

```bash
docker-compose start
```

### Stop and Remove Containers (Preserve Data)

```bash
docker-compose down
```

### Complete Cleanup (Remove Everything)

```bash
# WARNING: This will delete all data and containers
docker-compose down -v
rm -rf data/* logs/*
```

## Performance Optimization

### Resource Allocation

Edit `docker-compose.yml` to adjust resource limits:

```yaml
services:
  airflow-webserver:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
```

### Airflow Performance

Optimize DAG execution in `dags/beasiswa_dag.py`:

```python
# Increase parallelism
default_args = {
    'max_active_runs': 1,
    'max_active_tasks': 4,
    ...
}
```

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide for Python code
- Add comments for complex logic
- Update documentation for new features
- Test changes thoroughly before submitting

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

For issues, questions, or suggestions:

- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section

---

**Project Maintainer**: Data Engineering Team
**Last Updated**: October 2025
**Version**: 1.0.0