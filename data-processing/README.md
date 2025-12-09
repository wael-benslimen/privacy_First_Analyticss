# Data Processing - Differential Privacy Engine

This directory contains the data processing and differential privacy components for the Privacy First Analytics application.

## Structure

```
data-processing/
├── src/
│   ├── data_generation/  # Data generation utilities
│   ├── dp_engine/        # Differential privacy engine
│   └── tests/            # Unit tests
├── data/                 # Data files
├── analyses/             # Analysis outputs
├── integration/          # Integration components
└── requirements.txt      # Python dependencies
```

## Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Data Generation

Generate synthetic data for testing and analysis:
```bash
python src/data_generation/[script_name].py
```

### Differential Privacy Engine

Apply differential privacy mechanisms to your data:
```bash
python src/dp_engine/[engine_script].py
```

### Running Analyses

Execute analysis scripts:
```bash
python src/[analysis_script].py
```

## Integration

The integration directory contains components for integrating the DP engine with the backend API.

## Testing

Run tests:
```bash
python -m pytest src/tests/
```
