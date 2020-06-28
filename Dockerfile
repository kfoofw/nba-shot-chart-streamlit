FROM python:3.7.5-slim

# Copy all files into new folder directory
COPY . ./nba-shot-chart-streamlit/

# Move to new folder
WORKDIR ./nba-shot-chart-streamlit/

# Install requirements
RUN pip install -r requirements.txt

# Expose container port
EXPOSE 5000

# Run app
RUN streamlit run nba-shot-chart.py

