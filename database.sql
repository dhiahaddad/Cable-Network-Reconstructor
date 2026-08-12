CREATE TABLE test_cases (
    id INTEGER PRIMARY KEY autoincrement,
    network_name TEXT DEFAULT NULL,
    test_result TEXT DEFAULT NULL,
    processing_time float,
    network_id INT,
    identifiedPeaksNumber INTEGER DEFAULT NULL,
    unidentifiedPeaksNumber INTEGER DEFAULT NULL,
    totalPeaksNumber INTEGER DEFAULT NULL,
    is_complete TEXT DEFAULT NULL,
    reconstruction_level INT DEFAULT NULL
);

CREATE TABLE peaks (
    time float PRIMARY KEY,
    amplitude float
);

CREATE TABLE reference_junctions (
    id INT PRIMARY KEY,
    parent_id INT,
    distance_to_parent float,
    branches_number INT
);

CREATE TABLE reference_loads (
    id INT PRIMARY KEY,
    parent_id INT,
    distance_to_parent float,
    impedance float
);

CREATE TABLE reference_faults (
    id INT PRIMARY KEY,
    parent_id INT,
    distance_to_parent float,
    impedance float,
    fault_type TEXT
);

CREATE TABLE test_junctions (
    id INT PRIMARY KEY,
    parent_id INT,
    distance_to_parent float,
    branches_number INT
);

CREATE TABLE test_loads (
    id INT PRIMARY KEY,
    parent_id INT,
    distance_to_parent float,
    impedance INT
);

CREATE TABLE test_faults (
    id INT PRIMARY KEY,
    parent_id INT,
    distance_to_parent float,
    impedance INT,
    fault_type TEXT
);

CREATE TABLE config (
    logging_enabled INTEGER,
    MaxPathLength INTEGER,
    MIN_AMPLITUDE float,
    ORIGIN_ID INTEGER,
    EXCITATION_AMPLITUDE float,
    MAX_INPUT_NODE_TRAVERSALS INTEGER,
    CABLE_IMPEDANCE float,
    PEAK_V_TOLERANCE float,
    TIME_TOLERENCE float,
    MAX_BRANCHES_NUMBER INTEGER
);