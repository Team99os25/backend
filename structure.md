```
backend/
│
├── app/                              # Main application package
│   ├── __init__.py
│   ├── main.py                       # FastAPI application entry point
│   ├── config.py                     # Configuration settings
│   │
│   ├── api/                          # FastAPI API endpoints
│   │   ├── __init__.py
│   │   ├── dependencies.py           # Dependency injection definitions
│   │   ├── router.py                 # Main API router
│   │   ├── routes/                   # Route modules
│   │   │   ├── __init__.py
│   │   │   ├── employee.py           # Employee endpoints
│   │   │   ├── conversation.py       # Chat/conversation endpoints
│   │   │   ├── admin.py              # Admin endpoints
│   │   │   └── reports.py            # Reporting endpoints
│   │   │
│   │   └── middlewares/              # FastAPI middlewares
│   │       ├── __init__.py
│   │       ├── auth.py               # Authentication middleware
│   │       └── logging.py            # Logging middleware
│   │
│   ├── schemas/                      # Pydantic models for request/response
│   │   ├── __init__.py
│   │   ├── employee.py               # Employee schemas
│   │   ├── conversation.py           # Conversation schemas
│   │   ├── report.py                 # Report schemas
│   │   └── vibemeter.py              # Vibemeter schemas
│   │
│   ├── core/                         # Core business logic
│   │   ├── __init__.py
│   │   ├── employee_selector.py      # Algorithm to select employees for outreach
│   │   ├── data_correlator.py        # Correlates data from multiple sources
│   │   ├── threshold_manager.py      # Manages escalation thresholds
│   │   ├── insight_generator.py      # Generates insights from employee data
│   │   └── report_generator.py       # Generates daily reports
│   │
│   ├── ml/                           # Machine learning components
│   │   ├── __init__.py
│   │   ├── sentiment_analyzer.py     # Analyzes sentiment in responses
│   │   ├── nlp_processor.py          # Natural language processing
│   │   ├── model_manager.py          # Manages pre-trained models
│   │   ├── emotion_detector.py       # Detects emotions in text
│   │   └── feedback_classifier.py    # Classifies employee feedback
│   │
│   ├── db/                           # Database modules
│   │   ├── __init__.py
│   │   ├── session.py                # Database session management
│   │   ├── base.py                   # Base DB model
│   │   └── models/                   # SQLAlchemy ORM models
│   │       ├── __init__.py
│   │       ├── employee.py           # Employee model
│   │       ├── conversation.py       # Conversation model
│   │       ├── report.py             # Report model
│   │       ├── leave.py              # Leave data model
│   │       ├── activity.py           # Activity data model
│   │       ├── rewards.py            # Rewards data model
│   │       ├── performance.py        # Performance data model
│   │       ├── onboarding.py         # Onboarding data model
│   │       └── vibemeter.py          # Vibemeter data model
│   │
│   ├── crud/                         # CRUD operations
│   │   ├── __init__.py
│   │   ├── base.py                   # Base CRUD operations
│   │   ├── employee.py               # Employee operations
│   │   ├── vibemeter.py              # Vibemeter operations
│   │   ├── leave.py                  # Leave operations
│   │   ├── activity.py               # Activity operations
│   │   ├── rewards.py                # Rewards operations
│   │   ├── performance.py            # Performance operations
│   │   ├── onboarding.py             # Onboarding operations
│   │   ├── conversation.py           # Conversation operations
│   │   └── report.py                 # Report operations
│   │
│   ├── services/                     # Business services
│   │   ├── __init__.py
│   │   ├── conversation_service.py   # Manages conversation interactions
│   │   ├── notification_service.py   # Sends notifications to employees/HR
│   │   ├── analytics_service.py      # Provides analytics on employee data
│   │   ├── escalation_service.py     # Handles HR escalations
│   │   └── integration_service.py    # Integrates with external systems
│   │
│   ├── data_integration/             # Data integration components
│   │   ├── __init__.py
│   │   ├── data_connector.py         # Connects to various data sources
│   │   ├── data_transformer.py       # Transforms data for analysis
│   │   └── data_validator.py         # Validates incoming data
│   │
│   ├── question_bank/                # Question & Answer bank module
│   │   ├── __init__.py
│   │   ├── static_questions.py       # Predefined questions
│   │   ├── dynamic_questions.py      # Dynamically generated questions
│   │   ├── response_templates.py     # Response templates
│   │   ├── question_generator.py     # Generates personalized questions
│   │   └── context_manager.py        # Manages context for questions
│   │
│   ├── reporting/                    # Reporting capabilities
│   │   ├── __init__.py
│   │   ├── daily_report.py           # Daily report generation
│   │   ├── insights_generator.py     # Generates insights from data
│   │   ├── visualization.py          # Data visualization
│   │   ├── metrics_calculator.py     # Calculates performance metrics
│   │   └── trend_analyzer.py         # Analyzes trends in employee data
│   │
│   ├── ai_conversation/              # AI conversation handling
│   │   ├── __init__.py
│   │   ├── conversation_handler.py   # Manages conversation flow
│   │   ├── empathy_engine.py         # Provides empathetic responses
│   │   ├── context_manager.py        # Manages conversation context
│   │   ├── response_generator.py     # Generates AI responses
│   │   └── feedback_analyzer.py      # Analyzes employee feedback
│   │
│   ├── threshold_monitoring/         # Threshold monitoring
│   │   ├── __init__.py
│   │   ├── alert_system.py           # HR alert system
│   │   ├── threshold_config.py       # Alert thresholds
│   │   ├── escalation_rules.py       # Rules for escalating issues
│   │   └── priority_calculator.py    # Calculates issue priority
│   │
│   └── utils/                        # Utility functions
│       ├── __init__.py
│       ├── logger.py                 # Logging configuration
│       ├── validators.py             # Data validation utilities
│       ├── date_helpers.py           # Date manipulation helpers
│       └── helpers.py                # General helper functions
│
├── integration/                      # External integrations
│   ├── __init__.py
│   ├── teams_integration.py          # Microsoft Teams integration
│   └── slack_integration.py          # Slack integration
│
├── alembic/                          # Database migrations
│   ├── versions/
│   ├── env.py
│   └── alembic.ini
│
├── tests/                            # Test suite
│   ├── __init__.py
│   ├── conftest.py                   # Test configuration
│   ├── test_api/                     # API tests
│   ├── test_core/                    # Core logic tests
│   ├── test_ml/                      # Machine learning tests
│   ├── test_db/                      # Database tests
│   ├── test_services/                # Service tests
│   ├── test_data_integration/        # Data integration tests
│   ├── test_ai_conversation/         # AI conversation tests
│   └── test_question_bank/           # Question bank tests
│
├── scripts/                          # Utility scripts
│   ├── seed_db.py                    # Seed database with sample data
│   ├── generate_sample_data.py       # Generate test data
│   └── deploy.py                     # Deployment script
│
├── docs/                             # Documentation
│   ├── api/                          # API documentation
│   ├── architecture/                 # Architecture diagrams
│   ├── logic/                        # Logic documentation
│   │   ├── employee_selection.md     # Employee selection algorithm doc
│   │   ├── data_correlation.md       # Data correlation logic doc
│   │   └── thresholds.md             # Threshold rules documentation
│   └── deployment/                   # Deployment guides
│
├── sample_data/                      # Sample datasets
│   ├── leave_data.csv                # Leave data
│   ├── activity_data.csv             # Activity data
│   ├── rewards_data.csv              # Rewards data
│   ├── performance_data.csv          # Performance data
│   ├── onboarding_data.csv           # Onboarding data
│   └── vibemeter_data.csv            # Vibemeter data
│
├── deployment/                      # Deployment configurations
│   ├── docker/
│   │   ├── Dockerfile
│   │   └── docker-compose.yml
│   └── cloud/
│       └── deployment_guide.md
│
├── requirements.txt                 # Python dependencies
├── .env.example                     # Example environment variables
├── .gitignore                       # Git ignore file
├── README.md                        # Project documentation
└── pyproject.toml                   # Project metadata
```
Rest of the Database Schema needs to be thought upon:

### Some are predefined:

### 1. **vibemeter_data**
This table stores the vibe scores and emotional state of employees.

| Field Name       | Data Type | Description                                  |
|------------------|-----------|----------------------------------------------|
| `Employee_ID`    | INT       | Unique identifier for the employee           |
| `Response_Date`  | DATE      | The date when the vibe score was recorded    |
| `Vibe_Score`     | INT       | The numerical score representing the employee's vibe (e.g., 1-10) |
| `Emotion_Zone`   | VARCHAR   | The category or zone of the employee's emotion (e.g., Happy, Sad, Neutral) |

### 2. **reward_data**
This table keeps track of the rewards and points given to employees.

| Field Name       | Data Type | Description                                  |
|------------------|-----------|----------------------------------------------|
| `Employee_ID`    | INT       | Unique identifier for the employee           |
| `Award_Type`     | VARCHAR   | The type of award (e.g., Employee of the Month, Bonus) |
| `Award_Date`     | DATE      | The date when the award was given            |
| `Reward_Points`  | INT       | Points or value associated with the award    |

### 3. **performance_data**
This table records employee performance reviews and feedback.

| Field Name             | Data Type | Description                                   |
|------------------------|-----------|-----------------------------------------------|
| `Employee_ID`          | INT       | Unique identifier for the employee            |
| `Review_Period`        | VARCHAR   | The period of the review (e.g., Q1, Q2, 2025) |
| `Performance_Rating`   | INT       | The employee's performance rating (e.g., 1-5) |
| `Manager_Feedback`     | TEXT      | Feedback provided by the manager              |
| `Promotion_Consideration` | BOOLEAN | Whether the employee is under consideration for promotion (TRUE/FALSE) |

### 4. **onboarding_data**
This table tracks the onboarding process for new employees.

| Field Name               | Data Type | Description                                       |
|--------------------------|-----------|---------------------------------------------------|
| `Employee_ID`            | INT       | Unique identifier for the employee                |
| `Joining_Date`           | DATE      | The date the employee joined the company          |
| `Onboarding_Feedback`    | TEXT      | Feedback received from the employee about onboarding |
| `Mentor_Assigned`        | VARCHAR   | Name or ID of the mentor assigned to the employee |
| `Initial_Training_Completed` | BOOLEAN | Indicates if the employee has completed initial training (TRUE/FALSE) |

### 5. **leave_data**
This table contains the information about the employee's leave details.

| Field Name        | Data Type | Description                                      |
|-------------------|-----------|--------------------------------------------------|
| `Employee_ID`     | INT       | Unique identifier for the employee               |
| `Leave_Type`      | VARCHAR   | The type of leave (e.g., Sick, Vacation, Maternity) |
| `Leave_Days`      | INT       | Number of days taken for the leave               |
| `Leave_Start_Date`| DATE      | The start date of the leave                      |
| `Leave_End_Date`  | DATE      | The end date of the leave                        |

### 6. **activity_data**
This table tracks the daily activities of employees, including messages, emails, meetings, and work hours.

| Field Name               | Data Type | Description                                       |
|--------------------------|-----------|---------------------------------------------------|
| `Employee_ID`            | INT       | Unique identifier for the employee                |
| `Date`                   | DATE      | The date of the recorded activity                 |
| `Teams_Messages_Sent`    | INT       | The number of messages sent on Teams              |
| `Emails_Sent`            | INT       | The number of emails sent                         |
| `Meetings_Attended`      | INT       | The number of meetings attended                   |
| `Work_Hours`             | DECIMAL   | The number of hours worked during the day         |
