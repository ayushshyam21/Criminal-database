-- ============================================================================
-- SCRIPT 02: LOOKUP REFERENCE DATA SEEDING
-- Project: Criminal Case Management & Crime Analytics System (Project Evaluation)
-- Tables Populated: police_stations, iucr_codes
-- ============================================================================

USE crime_db;

-- 1. SEED POLICE STATIONS (Chicago Police Department Districts)
INSERT INTO police_stations (station_name, district_code, address, phone) VALUES
('1st District - Central', '001', '1718 S State St, Chicago, IL 60616', '312-745-4290'),
('2nd District - Wentworth', '002', '5101 S Wentworth Ave, Chicago, IL 60609', '312-747-8366'),
('3rd District - Grand Crossing', '003', '7040 S Cottage Grove Ave, Chicago, IL 60637', '312-747-8201'),
('4th District - South Chicago', '004', '2255 E 103rd St, Chicago, IL 60617', '312-747-7581'),
('5th District - Calumet', '005', '727 E 111th St, Chicago, IL 60628', '312-747-8210'),
('6th District - Gresham', '006', '7808 S Halsted St, Chicago, IL 60620', '312-745-3617'),
('7th District - Englewood', '007', '1438 W 63rd St, Chicago, IL 60636', '312-747-8380'),
('8th District - Chicago Lawn', '008', '3420 W 63rd St, Chicago, IL 60629', '312-747-8730'),
('9th District - Deering', '009', '3120 S Halsted St, Chicago, IL 60608', '312-747-8227'),
('10th District - Ogden', '010', '3315 W Ogden Ave, Chicago, IL 60623', '312-747-7511'),
('11th District - Harrison', '011', '3151 W Harrison St, Chicago, IL 60612', '312-746-8386'),
('12th District - Near West', '012', '1412 S Blue Island Ave, Chicago, IL 60608', '312-746-8396'),
('14th District - Shakespeare', '014', '2150 N California Ave, Chicago, IL 60647', '312-744-8290'),
('15th District - Austin', '015', '5701 W Madison St, Chicago, IL 60644', '312-743-1440'),
('16th District - Jefferson Park', '016', '5151 N Milwaukee Ave, Chicago, IL 60630', '312-742-4480'),
('17th District - Albany Park', '017', '4650 N Pulaski Rd, Chicago, IL 60630', '312-742-4410'),
('18th District - Near North', '018', '1160 N Larrabee St, Chicago, IL 60610', '312-742-5870'),
('19th District - Town Hall', '019', '850 W Addison St, Chicago, IL 60613', '312-744-8320'),
('20th District - Lincoln', '020', '5400 N Lincoln Ave, Chicago, IL 60625', '312-742-8714'),
('22nd District - Morgan Park', '022', '1900 W Monterey Ave, Chicago, IL 60643', '312-745-0710'),
('24th District - Rogers Park', '024', '6464 N Clark St, Chicago, IL 60626', '312-744-5907'),
('25th District - Grand Central', '025', '5555 W Grand Ave, Chicago, IL 60639', '312-746-8605')
ON DUPLICATE KEY UPDATE address = VALUES(address), phone = VALUES(phone);

-- 2. SEED CANONICAL IUCR CODES (Illinois Uniform Crime Reporting Reference Standards)
INSERT INTO iucr_codes (iucr_code, primary_type, description, fbi_code, is_active) VALUES
('0110', 'HOMICIDE', 'FIRST DEGREE MURDER', '01A', TRUE),
('0130', 'HOMICIDE', 'SECOND DEGREE MURDER', '01A', TRUE),
('0141', 'HOMICIDE', 'INVOLUNTARY MANSLAUGHTER', '01B', TRUE),
('0261', 'CRIM SEXUAL ASSAULT', 'AGGRAVATED: HANDGUN', '02', TRUE),
('0281', 'CRIM SEXUAL ASSAULT', 'NON-AGGRAVATED', '02', TRUE),
('031A', 'ROBBERY', 'ARMED: HANDGUN', '03', TRUE),
('031B', 'ROBBERY', 'ARMED: OTHER DANGEROUS WEAPON', '03', TRUE),
('0320', 'ROBBERY', 'STRONGARM - NO WEAPON', '03', TRUE),
('0325', 'ROBBERY', 'VEHICULAR HIJACKING', '03', TRUE),
('041A', 'BATTERY', 'AGGRAVATED: HANDGUN', '04B', TRUE),
('0420', 'BATTERY', 'AGGRAVATED: KNIFE/CUTTING INSTRUMENT', '04B', TRUE),
('0460', 'BATTERY', 'SIMPLE', '08B', TRUE),
('0486', 'BATTERY', 'DOMESTIC BATTERY SIMPLE', '08B', TRUE),
('051A', 'ASSAULT', 'AGGRAVATED: HANDGUN', '04A', TRUE),
('0520', 'ASSAULT', 'AGGRAVATED: KNIFE/CUTTING INSTRUMENT', '04A', TRUE),
('0560', 'ASSAULT', 'SIMPLE', '08A', TRUE),
('0610', 'BURGLARY', 'FORCIBLE ENTRY', '05', TRUE),
('0620', 'BURGLARY', 'UNLAWFUL ENTRY', '05', TRUE),
('0630', 'BURGLARY', 'ATTEMPTED FORCIBLE ENTRY', '05', TRUE),
('0810', 'THEFT', 'OVER $500', '06', TRUE),
('0820', 'THEFT', '$500 AND UNDER', '06', TRUE),
('0860', 'THEFT', 'RETAIL THEFT', '06', TRUE),
('0890', 'THEFT', 'FROM BUILDING', '06', TRUE),
('0910', 'MOTOR VEHICLE THEFT', 'AUTOMOBILE', '07', TRUE),
('0920', 'MOTOR VEHICLE THEFT', 'TRUCK, BUS, MOTORCYCLE', '07', TRUE),
('1020', 'ARSON', 'BY FIRE', '09', TRUE),
('1110', 'DECEPTIVE PRACTICE', 'BOGUS CHECK', '11', TRUE),
('1120', 'DECEPTIVE PRACTICE', 'FORGERY', '10', TRUE),
('1150', 'DECEPTIVE PRACTICE', 'CREDIT CARD FRAUD', '11', TRUE),
('1220', 'DECEPTIVE PRACTICE', 'THEFT OF LOST / MISLAID PROPERTY', '11', TRUE),
('1310', 'CRIMINAL DAMAGE', 'TO PROPERTY', '14', TRUE),
('1320', 'CRIMINAL DAMAGE', 'TO VEHICLE', '14', TRUE),
('1330', 'CRIMINAL TRESPASS', 'TO LAND', '26', TRUE),
('141A', 'WEAPONS VIOLATION', 'UNLAWFUL USE - HANDGUN', '15', TRUE),
('143A', 'WEAPONS VIOLATION', 'UNLAWFUL POSSESSION - HANDGUN', '15', TRUE),
('1811', 'NARCOTICS', 'POSS: CANNABIS 30GMS OR LESS', '18', TRUE),
('2024', 'NARCOTICS', 'POSS: HEROIN(WHITE)', '18', TRUE),
('2027', 'NARCOTICS', 'POSS: CRACK', '18', TRUE),
('2820', 'OTHER OFFENSE', 'TELEPHONE THREAT', '26', TRUE),
('2825', 'OTHER OFFENSE', 'HARASSMENT BY TELEPHONE', '26', TRUE)
ON DUPLICATE KEY UPDATE primary_type = VALUES(primary_type), description = VALUES(description);
