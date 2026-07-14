# STEP 2: SYSTEM ARCHITECTURE & DATABASE DESIGN
## Enterprise-Grade Personal XAUUSD Trading System

---

## 🎯 STEP 2 OVERVIEW

**Phase:** System Architecture & Technical Foundation
**Duration:** 2-3 weeks (14-21 days)
**Effort:** 25-35 hours
**Objective:** Design scalable, reliable trading system architecture
**Scope:** Database design, API specifications, system components

**Prerequisites:**
- ✅ Step 1 Complete
- ✅ Personal documentation created
- ✅ Risk tolerance assessed
- ✅ Trading rules documented

---

## 📊 SYSTEM ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────┐
│                   YOUR XAUUSD TRADING SYSTEM                │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            FRONTEND LAYER                           │   │
│  │  ├─ React Dashboard (Real-time P&L)                │   │
│  │  ├─ Trading Controls (Start/Stop)                  │   │
│  │  ├─ Performance Charts                             │   │
│  │  └─ Risk Metrics Display                           │   │
│  └─────────────────────────────────────────────────────┘   │
│                          ↓                                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         API LAYER (FastAPI)                         │   │
│  │  ├─ REST Endpoints (GET/POST)                      │   │
│  │  ├─ WebSocket (Real-time updates)                  │   │
│  │  ├─ Authentication/Authorization                    │   │
│  │  └─ Rate Limiting & Validation                     │   │
│  └─────────────────────────────────────────────────────┘   │
│         ↓                ↓                    ↓              │
│  ┌───────────┐  ┌──────────────┐  ┌──────────────────┐    │
│  │ Algorithm │  │ Risk Engine  │  │ Data Processor   │    │
│  │ Module    │  │ (Kill Switch)│  │ (Market Data)    │    │
│  │           │  │              │  │                  │    │
│  │ ├─Trading │  │ ├─Limits     │  │ ├─Feed Handler   │    │
│  │ │Strategy │  │ │Enforcement │  │ │Validation      │    │
│  │ │Logic    │  │ │            │  │ │Indicator Calc  │    │
│  │ │          │  │ ├─Kill Switch│  │ │                │    │
│  │ ├─Signal  │  │ │Triggers    │  │ ├─Data Storage   │    │
│  │ │Generation│  │ │            │  │ │                │    │
│  │ │          │  │ └─Manual     │  │ └─Cache (Redis) │    │
│  │ └─Confidence│ │Override     │  │                  │    │
│  │  Scoring   │  │            │  │                  │    │
│  └───────────┘  └──────────────┘  └──────────────────┘    │
│         ↓              ↓                    ↓               │
│  ┌───────────────────────────────────────────────────┐    │
│  │    MESSAGE QUEUE (RabbitMQ)                       │    │
│  │  ├─ Trade Events                                  │    │
│  │  ├─ Risk Alerts                                   │    │
│  │  ├─ System Notifications                          │    │
│  │  └─ Audit Trail Events                            │    │
│  └───────────────────────────────────────────────────┘    │
│         ↓              ↓              ↓                     │
│  ┌────────────┐ ┌──────────────┐ ┌──────────────┐         │
│  │ PostgreSQL │ │ Broker API   │ │ Notification │         │
│  │ Database   │ │ Connector    │ │ Service      │         │
│  │            │ │              │ │              │         │
│  │ ├─Trades   │ │ ├─Order Mgmt │ │ ├─Email      │         │
│  │ ├─Account  │ │ │Execution   │ │ ├─SMS        │         │
│  │ ├─Signals  │ │ │            │ │ ├─Telegram   │         │
│  │ ├─Audit    │ │ ├─Position   │ │ └─Logs       │         │
│  │ │Trail     │ │ │Tracking    │ │              │         │
│  │ └─Metrics  │ │ └─Quotes     │ │              │         │
│  └────────────┘ └──────────────┘ └──────────────┘         │
│         ↓              ↓              ↓                     │
│  ┌───────────────────────────────────────────────────┐    │
│  │    MONITORING LAYER (Prometheus + Grafana)        │    │
│  │  ├─ System Health                                 │    │
│  │  ├─ Performance Metrics                           │    │
│  │  ├─ Alert Management                              │    │
│  │  └─ Log Aggregation                               │    │
│  └───────────────────────────────────────────────────┘    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗄️ DATABASE SCHEMA DESIGN

### Core Tables

#### 1. **accounts** - Account Information
```sql
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    broker_name VARCHAR(100),
    account_number VARCHAR(100) UNIQUE,
    account_type VARCHAR(20), -- 'live', 'demo', 'paper'
    currency VARCHAR(3) DEFAULT 'USD',
    
    -- Account Status
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'suspended', 'closed'
    is_automated BOOLEAN DEFAULT FALSE,
    
    -- Initial Setup
    initial_balance DECIMAL(15, 2),
    current_balance DECIMAL(15, 2),
    
    -- Risk Parameters
    max_daily_loss DECIMAL(15, 2),
    max_weekly_loss DECIMAL(15, 2),
    max_monthly_loss DECIMAL(15, 2),
    max_drawdown_percent DECIMAL(5, 2),
    max_concurrent_trades INTEGER DEFAULT 3,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_accounts_user_id ON accounts(user_id);
CREATE INDEX idx_accounts_broker ON accounts(broker_name);
```

#### 2. **trades** - Individual Trades
```sql
CREATE TABLE trades (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL,
    
    -- Trade Identification
    trade_id VARCHAR(50) UNIQUE,
    symbol VARCHAR(10), -- 'XAUUSD'
    
    -- Entry
    entry_time TIMESTAMP,
    entry_price DECIMAL(10, 5),
    entry_reason VARCHAR(500), -- Algorithm reason
    entry_confidence DECIMAL(3, 2), -- 0.00 to 1.00
    
    -- Position
    position_type VARCHAR(10), -- 'LONG', 'SHORT'
    position_size DECIMAL(10, 5),
    
    -- Risk Parameters
    stop_loss DECIMAL(10, 5),
    take_profit DECIMAL(10, 5),
    max_risk_dollars DECIMAL(15, 2),
    
    -- Exit
    exit_time TIMESTAMP,
    exit_price DECIMAL(10, 5),
    exit_type VARCHAR(20), -- 'TP', 'SL', 'MANUAL', 'SYSTEM'
    exit_reason VARCHAR(500),
    
    -- Performance
    pips_profit DECIMAL(10, 5),
    dollars_profit DECIMAL(15, 2),
    profit_percent DECIMAL(6, 2),
    commission DECIMAL(15, 2),
    slippage DECIMAL(10, 5),
    
    -- Trade Metrics
    holding_minutes INTEGER,
    max_favorable_excursion DECIMAL(10, 5),
    max_adverse_excursion DECIMAL(10, 5),
    
    -- Status
    status VARCHAR(20) DEFAULT 'closed', -- 'open', 'closed'
    
    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (account_id) REFERENCES accounts(id)
);

CREATE INDEX idx_trades_account_id ON trades(account_id);
CREATE INDEX idx_trades_entry_time ON trades(entry_time);
CREATE INDEX idx_trades_status ON trades(status);
```

#### 3. **signals** - Trading Signals Generated
```sql
CREATE TABLE signals (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL,
    
    -- Signal Identification
    signal_id VARCHAR(50) UNIQUE,
    symbol VARCHAR(10),
    signal_type VARCHAR(20), -- 'BUY', 'SELL', 'EXIT'
    
    -- Signal Generation
    generated_at TIMESTAMP,
    confidence_score DECIMAL(3, 2),
    
    -- Indicators
    indicators_data JSONB, -- Store JSON of all indicator values
    market_regime VARCHAR(50), -- 'UPTREND', 'DOWNTREND', 'RANGING'
    
    -- Action Taken
    action_taken VARCHAR(20), -- 'EXECUTED', 'REJECTED', 'PENDING'
    action_reason VARCHAR(500),
    
    -- Trade Linked
    trade_id INTEGER,
    
    -- System State
    account_balance DECIMAL(15, 2),
    equity DECIMAL(15, 2),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (account_id) REFERENCES accounts(id),
    FOREIGN KEY (trade_id) REFERENCES trades(id)
);

CREATE INDEX idx_signals_account_id ON signals(account_id);
CREATE INDEX idx_signals_generated_at ON signals(generated_at);
```

#### 4. **market_data** - XAUUSD Market Quotes
```sql
CREATE TABLE market_data (
    id SERIAL PRIMARY KEY,
    
    -- Quote Data
    timestamp TIMESTAMP UNIQUE,
    bid DECIMAL(10, 5),
    ask DECIMAL(10, 5),
    last_price DECIMAL(10, 5),
    
    -- Volume & Liquidity
    bid_volume DECIMAL(15, 2),
    ask_volume DECIMAL(15, 2),
    
    -- Spread
    spread_pips DECIMAL(5, 2),
    
    -- OHLC (for 1-minute bars)
    open_1m DECIMAL(10, 5),
    high_1m DECIMAL(10, 5),
    low_1m DECIMAL(10, 5),
    close_1m DECIMAL(10, 5),
    
    -- OHLC (for 5-minute bars)
    open_5m DECIMAL(10, 5),
    high_5m DECIMAL(10, 5),
    low_5m DECIMAL(10, 5),
    close_5m DECIMAL(10, 5),
    
    -- OHLC (for hourly bars)
    open_1h DECIMAL(10, 5),
    high_1h DECIMAL(10, 5),
    low_1h DECIMAL(10, 5),
    close_1h DECIMAL(10, 5),
    
    -- Source
    source VARCHAR(50), -- 'Broker1', 'Broker2', 'DataProvider'
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_market_data_timestamp ON market_data(timestamp);
CREATE INDEX idx_market_data_bid_ask ON market_data(bid, ask);
```

#### 5. **audit_trail** - Complete System Audit Log
```sql
CREATE TABLE audit_trail (
    id SERIAL PRIMARY KEY,
    
    -- Event Information
    account_id INTEGER,
    event_type VARCHAR(50), -- 'TRADE_ENTRY', 'TRADE_EXIT', 'ALERT', 'ERROR'
    event_severity VARCHAR(20), -- 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    
    -- Event Details
    event_description VARCHAR(1000),
    event_data JSONB, -- Flexible storage of event specifics
    
    -- Trade Reference
    trade_id INTEGER,
    signal_id INTEGER,
    
    -- System State
    system_status VARCHAR(50),
    account_equity DECIMAL(15, 2),
    account_drawdown DECIMAL(6, 2),
    
    -- Timestamps
    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (account_id) REFERENCES accounts(id),
    FOREIGN KEY (trade_id) REFERENCES trades(id),
    FOREIGN KEY (signal_id) REFERENCES signals(id)
);

CREATE INDEX idx_audit_trail_account_id ON audit_trail(account_id);
CREATE INDEX idx_audit_trail_event_timestamp ON audit_trail(event_timestamp);
CREATE INDEX idx_audit_trail_event_type ON audit_trail(event_type);
```

#### 6. **system_metrics** - Performance Metrics
```sql
CREATE TABLE system_metrics (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL,
    
    -- Time Period
    metric_date DATE,
    
    -- Performance
    total_trades INTEGER,
    winning_trades INTEGER,
    losing_trades INTEGER,
    win_rate DECIMAL(5, 2),
    
    -- Profit/Loss
    gross_profit DECIMAL(15, 2),
    gross_loss DECIMAL(15, 2),
    net_profit DECIMAL(15, 2),
    total_commission DECIMAL(15, 2),
    
    -- Risk Metrics
    max_drawdown DECIMAL(6, 2),
    average_loss DECIMAL(15, 2),
    average_win DECIMAL(15, 2),
    profit_factor DECIMAL(5, 2),
    
    -- Account Metrics
    starting_balance DECIMAL(15, 2),
    ending_balance DECIMAL(15, 2),
    daily_return DECIMAL(6, 2),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (account_id) REFERENCES accounts(id)
);

CREATE INDEX idx_metrics_account_date ON system_metrics(account_id, metric_date);
```

#### 7. **alerts** - System Alerts & Notifications
```sql
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL,
    
    -- Alert Info
    alert_type VARCHAR(50), -- 'LOSS_LIMIT', 'DRAWDOWN_LIMIT', 'SYSTEM_ERROR'
    alert_severity VARCHAR(20), -- 'INFO', 'WARNING', 'CRITICAL'
    
    -- Alert Details
    alert_message VARCHAR(1000),
    alert_data JSONB,
    
    -- Status
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'acknowledged', 'resolved'
    acknowledged_at TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (account_id) REFERENCES accounts(id)
);

CREATE INDEX idx_alerts_account_id ON alerts(account_id);
CREATE INDEX idx_alerts_severity ON alerts(alert_severity);
```

---

## 🔌 API ENDPOINTS SPECIFICATION

### Authentication
```
POST /api/v1/auth/login
├─ Request: { username, password }
└─ Response: { access_token, expires_in }

POST /api/v1/auth/logout
└─ Request: { access_token }
```

### Account Management
```
GET /api/v1/accounts/{account_id}
├─ Returns: Account details, balance, equity, drawdown

PUT /api/v1/accounts/{account_id}
├─ Update risk parameters, status
└─ Returns: Updated account

GET /api/v1/accounts/{account_id}/balance
└─ Returns: Current balance, equity, available margin

POST /api/v1/accounts/{account_id}/start-trading
└─ Start automated trading

POST /api/v1/accounts/{account_id}/stop-trading
└─ Stop automated trading (graceful shutdown)

POST /api/v1/accounts/{account_id}/emergency-stop
└─ Emergency kill switch (immediate stop)
```

### Trading
```
GET /api/v1/trades/{account_id}
├─ Query: ?status=open|closed&limit=50&offset=0
└─ Returns: List of trades with pagination

GET /api/v1/trades/{trade_id}
└─ Returns: Detailed trade information

POST /api/v1/trades/{account_id}/manual-entry
├─ Request: { symbol, price, size, side, stop_loss, take_profit }
└─ Returns: Trade details

POST /api/v1/trades/{trade_id}/manual-exit
├─ Request: { price, reason }
└─ Returns: Exit confirmation

GET /api/v1/positions/{account_id}
└─ Returns: Currently open positions
```

### Signals
```
GET /api/v1/signals/{account_id}
├─ Query: ?status=executed|rejected&limit=100
└─ Returns: List of generated signals

GET /api/v1/signals/{signal_id}
└─ Returns: Signal details and decision reasoning
```

### Performance Metrics
```
GET /api/v1/metrics/{account_id}/daily
├─ Query: ?date=YYYY-MM-DD
└─ Returns: Daily performance metrics

GET /api/v1/metrics/{account_id}/summary
├─ Query: ?period=week|month|year
└─ Returns: Performance summary

GET /api/v1/metrics/{account_id}/statistics
└─ Returns: Win rate, profit factor, Sharpe ratio, etc.
```

### Market Data
```
GET /api/v1/market/xauusd
├─ Returns: Current bid/ask/last price
└─ Frequency: Real-time via WebSocket

GET /api/v1/market/xauusd/ohlc
├─ Query: ?timeframe=1m|5m|1h&bars=100
└─ Returns: OHLC bars
```

### Alerts & Notifications
```
GET /api/v1/alerts/{account_id}
├─ Query: ?status=active|acknowledged
└─ Returns: List of alerts

PUT /api/v1/alerts/{alert_id}/acknowledge
└─ Acknowledge an alert

GET /api/v1/notifications
├─ Returns: Recent notifications
└─ Via WebSocket for real-time updates
```

### Audit Trail
```
GET /api/v1/audit-trail/{account_id}
├─ Query: ?start_date=&end_date=&event_type=
└─ Returns: Audit trail entries (sorted by timestamp)
```

---

## 🔐 DATA SECURITY SPECIFICATIONS

### Encryption
```python
# Database Passwords
ENCRYPTED_IN: .env file (NOT in git)
ENCRYPTION_METHOD: AES-256

# API Keys
ENCRYPTED_IN: HashiCorp Vault or .env
ROTATION_SCHEDULE: Every 90 days

# Database Connection
ENCRYPTION: TLS 1.2+ (in transit)
DATABASE: Encryption at rest (AES-256)

# Data Classification
PUBLIC: Market data, generic metrics
SENSITIVE: Account details, positions, trades
CONFIDENTIAL: API keys, passwords, personal data
```

### Access Control
```
Role: User (Personal Trader)
├─ Read: Own account data, own trades, own signals
├─ Write: Manual trade entries, settings
├─ Delete: None (only archive via UI)
└─ Admin: Full access to own account

Role: System
├─ Read: All data for system operations
├─ Write: Audit trail, signals, trades
└─ Delete: Aged data archival only
```

---

## 📊 COMPONENT SPECIFICATIONS

### 1. **Algorithm Module**
```python
class TradingAlgorithm:
    def __init__(self):
        self.indicators = {}
        self.confidence_threshold = 0.70
        
    def calculate_signals(self, market_data) -> Signal:
        # Calculate all technical indicators
        # Generate entry/exit signals
        # Calculate confidence score (0.0 - 1.00)
        # Return signal with reasoning
        pass
        
    def position_sizing(self, account_equity, risk_per_trade) -> float:
        # Calculate position size based on
        # - Account equity
        # - Risk per trade (% or $)
        # - Stop loss distance
        pass
```

### 2. **Risk Management Engine**
```python
class RiskManager:
    def __init__(self, account):
        self.daily_loss_limit = account.max_daily_loss
        self.weekly_loss_limit = account.max_weekly_loss
        self.monthly_loss_limit = account.max_monthly_loss
        self.max_drawdown = account.max_drawdown_percent
        
    def check_daily_limit(self, current_loss) -> bool:
        return current_loss < self.daily_loss_limit
        
    def check_drawdown_limit(self, equity, peak_equity) -> bool:
        drawdown = (peak_equity - equity) / peak_equity * 100
        return drawdown < self.max_drawdown
        
    def should_kill_switch_trigger(self) -> bool:
        # Check all limits and conditions
        # Return True if any limit exceeded
        pass
```

### 3. **Order Execution Engine**
```python
class OrderExecutor:
    def __init__(self, broker_connector):
        self.broker = broker_connector
        self.max_retries = 3
        self.retry_delay = 5  # seconds
        
    def execute_market_order(self, order: Order) -> Trade:
        # Place order with broker
        # Handle rejections with retry logic
        # Create trade record
        # Log to audit trail
        pass
        
    def execute_exit_order(self, trade: Trade) -> Trade:
        # Close trade at current market
        # Update trade record
        # Calculate P&L
        pass
```

### 4. **Data Processor**
```python
class DataProcessor:
    def __init__(self, data_source):
        self.source = data_source
        self.cache = Redis()
        
    def process_market_data(self, quote) -> None:
        # Validate quote data
        # Update OHLC bars
        # Trigger indicator calculations
        # Cache for fast access
        pass
```

---

## 📈 TECHNOLOGY STACK DETAILS

### Backend
```
Framework:    FastAPI (async Python)
Version:      3.9+
Database:     PostgreSQL 12+
Cache:        Redis 6.0+
Message Queue: RabbitMQ 3.8+
Task Queue:   Celery
```

### Frontend
```
Framework:    React 18+
TypeScript:   4.5+
State:        Redux Toolkit
Charts:       TradingView Lightweight Charts
UI:           Material-UI
```

### DevOps
```
Containerization: Docker + Docker Compose
Orchestration:    Kubernetes (optional)
Monitoring:       Prometheus + Grafana
Logging:          ELK Stack
CI/CD:            GitHub Actions
```

---

## 🚀 STEP 2 ACTION ITEMS

### Week 1: Database & Data Model

**Task 2.1: Create Database Schema**
- [ ] PostgreSQL installation
- [ ] Database creation script
- [ ] All 7 tables created
- [ ] Indexes optimized
- [ ] Backup procedure setup
- Time estimate: 4-5 hours

**Task 2.2: Implement ORM Models**
- [ ] SQLAlchemy models
- [ ] Relationships defined
- [ ] Migrations setup
- [ ] Validation rules
- Time estimate: 3-4 hours

### Week 2: API Design & Specifications

**Task 2.3: Define API Endpoints**
- [ ] OpenAPI/Swagger spec
- [ ] Request/response schemas
- [ ] Error handling spec
- [ ] Rate limiting rules
- Time estimate: 4-5 hours

**Task 2.4: Security Design**
- [ ] Authentication flow
- [ ] Authorization rules
- [ ] Encryption specifications
- [ ] Audit logging requirements
- Time estimate: 3-4 hours

### Week 3: Component Architecture

**Task 2.5: Component Design**
- [ ] Algorithm module structure
- [ ] Risk management design
- [ ] Order execution flow
- [ ] Data processor pipeline
- Time estimate: 5-6 hours

**Task 2.6: Integration Design**
- [ ] Component interactions
- [ ] Message queue design
- [ ] Error handling patterns
- [ ] Fallback procedures
- Time estimate: 4-5 hours

---

## ✅ STEP 2 DELIVERABLES

By end of Step 2, you will have:

- [ ] **Database Schema** - All 7 tables designed and documented
- [ ] **ORM Models** - SQLAlchemy models with relationships
- [ ] **API Specification** - Complete OpenAPI/Swagger documentation
- [ ] **Component Architecture** - Detailed design of all modules
- [ ] **Security Specification** - Authentication, authorization, encryption
- [ ] **Integration Design** - How components communicate
- [ ] **Development Roadmap** - Step 3 implementation plan
- [ ] **Technical Documentation** - Complete system design document

---

## 📝 NEXT: STEP 3 PREVIEW

**STEP 3: Development & Integration (Week 6-11)**

Will include:
- Core system development
- API implementation
- Database integration
- Risk management system
- Order execution
- Real-time monitoring
- Complete testing

---

**Status:** ✅ STEP 2 Ready to Begin

**Start Date:** Upon completion of Step 1 action items

**Expected Timeline:** 2-3 weeks

**Next:** Follow STEP 2 action items detailed above

