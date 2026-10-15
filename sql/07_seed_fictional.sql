-- ============================================================================
-- SCRIPT 07: SYNTHETIC FICTIONAL DEMONSTRATION DATA SEEDING
-- Project: Criminal Case Management & Crime Analytics System (Project Evaluation)
-- Target Database: crime_db
-- Integrity: All case and persona records are strictly marked is_fictional = TRUE
-- Passwords: All demo accounts use 'DemoPass123!' (Werkzeug scrypt hash)
-- ============================================================================

USE crime_db;

-- 1. SEED SYSTEM USERS (Admin, Officers, Investigators across Stations)
INSERT INTO users (user_id, station_id, username, email, password_hash, role, full_name, badge_number, is_active) VALUES
(1, 1, 'admin_sys', 'admin@precinct.local', 'scrypt:32768:8:1$AEmYhJiklwBmMbF4$53213f13902622996701bee4e34ea32e8f6c8b160dc3d7909aed3799642ba33486522e9ed35207d2538d56bea062ca6c1ccbe745fbfbc4fce01110da5b70d0be', 'Admin', 'Chief Eleanor Vance', 'BADGE-ADM-01', TRUE),
(2, 1, 'officer_carter', 'm.carter@precinct.local', 'scrypt:32768:8:1$AEmYhJiklwBmMbF4$53213f13902622996701bee4e34ea32e8f6c8b160dc3d7909aed3799642ba33486522e9ed35207d2538d56bea062ca6c1ccbe745fbfbc4fce01110da5b70d0be', 'Officer', 'Officer Marcus Carter', 'BADGE-OFF-101', TRUE),
(3, 1, 'officer_ramirez', 's.ramirez@precinct.local', 'scrypt:32768:8:1$AEmYhJiklwBmMbF4$53213f13902622996701bee4e34ea32e8f6c8b160dc3d7909aed3799642ba33486522e9ed35207d2538d56bea062ca6c1ccbe745fbfbc4fce01110da5b70d0be', 'Officer', 'Officer Sofia Ramirez', 'BADGE-OFF-102', TRUE),
(4, 18, 'officer_jordan', 'l.jordan@precinct.local', 'scrypt:32768:8:1$AEmYhJiklwBmMbF4$53213f13902622996701bee4e34ea32e8f6c8b160dc3d7909aed3799642ba33486522e9ed35207d2538d56bea062ca6c1ccbe745fbfbc4fce01110da5b70d0be', 'Officer', 'Officer Lucas Jordan', 'BADGE-OFF-103', TRUE),
(5, 1, 'investigator_chen', 'd.chen@precinct.local', 'scrypt:32768:8:1$AEmYhJiklwBmMbF4$53213f13902622996701bee4e34ea32e8f6c8b160dc3d7909aed3799642ba33486522e9ed35207d2538d56bea062ca6c1ccbe745fbfbc4fce01110da5b70d0be', 'Investigator', 'Det. David Chen', 'BADGE-INV-201', TRUE),
(6, 1, 'investigator_hayes', 'r.hayes@precinct.local', 'scrypt:32768:8:1$AEmYhJiklwBmMbF4$53213f13902622996701bee4e34ea32e8f6c8b160dc3d7909aed3799642ba33486522e9ed35207d2538d56bea062ca6c1ccbe745fbfbc4fce01110da5b70d0be', 'Investigator', 'Det. Rachel Hayes', 'BADGE-INV-202', TRUE),
(7, 19, 'investigator_kowalski', 'm.kowalski@precinct.local', 'scrypt:32768:8:1$AEmYhJiklwBmMbF4$53213f13902622996701bee4e34ea32e8f6c8b160dc3d7909aed3799642ba33486522e9ed35207d2538d56bea062ca6c1ccbe745fbfbc4fce01110da5b70d0be', 'Investigator', 'Det. Michael Kowalski', 'BADGE-INV-203', TRUE)
ON DUPLICATE KEY UPDATE full_name = VALUES(full_name);

-- 2. SEED FICTIONAL PERSONS (Demonstration Personas - All is_fictional = TRUE)
INSERT INTO persons (person_id, first_name, last_name, date_of_birth, gender, phone_contact, address_line, is_fictional) VALUES
(1, 'Demo-Suspect', 'Sterling', '1988-04-12', 'Male', '312-555-0101', 'Fictional 101 State St, Chicago, IL', TRUE),
(2, 'Demo-Victim', 'Montgomery', '1992-09-24', 'Female', '312-555-0102', 'Fictional 202 Michigan Ave, Chicago, IL', TRUE),
(3, 'Demo-Witness', 'Patel', '1985-11-15', 'Non-Binary', '312-555-0103', 'Fictional 303 Halsted St, Chicago, IL', TRUE),
(4, 'Demo-Suspect', 'Vargas', '1995-02-03', 'Male', '312-555-0104', 'Fictional 404 Western Ave, Chicago, IL', TRUE),
(5, 'Demo-Victim', 'Gallagher', '1979-07-19', 'Male', '312-555-0105', 'Fictional 505 Belmont Ave, Chicago, IL', TRUE),
(6, 'Demo-Witness', 'Zhao', '1998-05-30', 'Female', '312-555-0106', 'Fictional 606 Clark St, Chicago, IL', TRUE),
(7, 'Demo-Suspect', 'OConnor', '1983-12-08', 'Male', '312-555-0107', 'Fictional 707 Pulaski Rd, Chicago, IL', TRUE),
(8, 'Demo-Victim', 'Washington', '1990-01-14', 'Female', '312-555-0108', 'Fictional 808 63rd St, Chicago, IL', TRUE),
(9, 'Demo-Witness', 'Dubois', '1975-08-22', 'Female', '312-555-0109', 'Fictional 909 Broadway, Chicago, IL', TRUE),
(10, 'Demo-Person', 'Alvarez', '2001-03-11', 'Male', '312-555-0110', 'Fictional 1010 Madison St, Chicago, IL', TRUE),
(11, 'Demo-Suspect', 'Novak', '1987-06-18', 'Male', '312-555-0111', 'Fictional 1111 Milwaukee Ave, Chicago, IL', TRUE),
(12, 'Demo-Victim', 'Kowalke', '1994-10-05', 'Female', '312-555-0112', 'Fictional 1212 Grand Ave, Chicago, IL', TRUE),
(13, 'Demo-Witness', 'Thornton', '1982-09-17', 'Male', '312-555-0113', 'Fictional 1313 Damen Ave, Chicago, IL', TRUE),
(14, 'Demo-Suspect', 'Sinclair', '1991-04-29', 'Female', '312-555-0114', 'Fictional 1414 Ashland Ave, Chicago, IL', TRUE),
(15, 'Demo-Victim', 'Mercer', '1986-12-01', 'Male', '312-555-0115', 'Fictional 1515 Roosevelt Rd, Chicago, IL', TRUE)
ON DUPLICATE KEY UPDATE first_name = VALUES(first_name);

-- 3. SEED 50 CRIMINAL CASES (Respects chk_cases_closure_consistency)
-- Statuses: Open, Under Investigation, Pending Review, Closed, Cold Case
INSERT INTO cases (case_id, case_number, station_id, title, description, case_type, status, priority, incident_location, date_reported, date_closed, created_by, is_fictional) VALUES
(1, 'CASE-2026-0001', 1, 'Commercial Burglary at Downtown Retailer', 'Forced entry via rear security doors after operating hours. Inventory losses reported.', 'Burglary', 'Under Investigation', 'High', '100 N State St, Chicago, IL', '2026-01-05 02:30:00', NULL, 2, TRUE),
(2, 'CASE-2026-0002', 1, 'Armed Bank Robbery at Financial Square', 'Suspect presented weapon and demand note to teller. Security footage obtained.', 'Robbery', 'Under Investigation', 'Critical', '200 S LaSalle St, Chicago, IL', '2026-01-08 14:15:00', NULL, 2, TRUE),
(3, 'CASE-2026-0003', 1, 'Cryptocurrency Fraud & Identity Theft', 'Elderly victim defrauded of life savings through spoofed banking portal.', 'Fraud', 'Closed', 'Medium', '350 E Cermak Rd, Chicago, IL', '2026-01-10 11:00:00', '2026-02-15 16:30:00', 3, TRUE),
(4, 'CASE-2026-0004', 18, 'Aggravated Assault near Riverfront Promenade', 'Physical altercation following verbal argument. Weapon recovered at scene.', 'Assault', 'Under Investigation', 'High', '400 N Michigan Ave, Chicago, IL', '2026-01-14 23:45:00', NULL, 4, TRUE),
(5, 'CASE-2026-0005', 18, 'Luxury Motor Vehicle Theft from Secure Garage', 'High-end SUV stolen using signal relay amplifier attack on key fob.', 'Theft', 'Closed', 'Low', '800 N Lake Shore Dr, Chicago, IL', '2026-01-18 04:00:00', '2026-02-02 09:00:00', 4, TRUE),
(6, 'CASE-2026-0006', 19, 'Residential Burglary in Lakeview District', 'Jewelry and electronics stolen while homeowners were out of town.', 'Burglary', 'Cold Case', 'Medium', '3200 N Clark St, Chicago, IL', '2026-01-22 18:20:00', NULL, 2, TRUE),
(7, 'CASE-2026-0007', 1, 'Cyber Extortion & Ransomware Attack', 'Municipal logistics firm networks locked with encrypted ransomware.', 'Cybercrime', 'Under Investigation', 'Critical', '500 W Madison St, Chicago, IL', '2026-01-25 08:30:00', NULL, 3, TRUE),
(8, 'CASE-2026-0008', 2, 'Commercial Warehouse Narcotics Distribution', 'Large shipment of illicit controlled substances intercepted during transit.', 'Narcotics', 'Pending Review', 'High', '5100 S Wentworth Ave, Chicago, IL', '2026-02-01 19:10:00', NULL, 2, TRUE),
(9, 'CASE-2026-0009', 3, 'Homicide Investigation on South Cottage Grove', 'Fatal gunshot wound resulting from street confrontation.', 'Homicide', 'Under Investigation', 'Critical', '7100 S Cottage Grove Ave, Chicago, IL', '2026-02-05 21:50:00', NULL, 2, TRUE),
(10, 'CASE-2026-0010', 1, 'Counterfeit Currency Circulation in Loop', 'Multiple counterfeit $100 bills passed at downtown restaurants.', 'Fraud', 'Closed', 'Low', '150 N Dearborn St, Chicago, IL', '2026-02-08 12:40:00', '2026-03-01 14:00:00', 3, TRUE),
(11, 'CASE-2026-0011', 11, 'Aggravated Vehicular Hijacking', 'Victim carjacked at gunpoint while parked at filling station.', 'Robbery', 'Under Investigation', 'Critical', '3200 W Harrison St, Chicago, IL', '2026-02-12 22:15:00', NULL, 2, TRUE),
(12, 'CASE-2026-0012', 12, 'Vandalism and Property Damage to Rail Facility', 'Extensive graffiti and destruction of rail transit signaling boxes.', 'Other', 'Closed', 'Low', '1400 S Blue Island Ave, Chicago, IL', '2026-02-15 03:00:00', '2026-02-28 11:30:00', 3, TRUE),
(13, 'CASE-2026-0013', 18, 'Retail Shoplifting Ring at Gold Coast Plaza', 'Coordinated shoplifting crew removing luxury designer garments.', 'Theft', 'Pending Review', 'Medium', '900 N Michigan Ave, Chicago, IL', '2026-02-18 16:30:00', NULL, 4, TRUE),
(14, 'CASE-2026-0014', 19, 'Physical Battery outside Wrigley Field Pub', 'Patron assaulted in parking lot following sports broadcast.', 'Assault', 'Closed', 'Medium', '3600 N Clark St, Chicago, IL', '2026-02-22 01:15:00', '2026-03-10 17:00:00', 2, TRUE),
(15, 'CASE-2026-0015', 1, 'Unauthorized Access to Medical Database', 'Ex-employee accessed and exfiltrated confidential patient records.', 'Cybercrime', 'Under Investigation', 'High', '250 E Superior St, Chicago, IL', '2026-02-25 10:00:00', NULL, 3, TRUE),
(16, 'CASE-2026-0016', 7, 'Firearms Trafficking & Illegal Possession', 'Seizure of modified automatic weapons and tactical equipment.', 'Other', 'Under Investigation', 'Critical', '6400 S Halsted St, Chicago, IL', '2026-03-01 20:00:00', NULL, 2, TRUE),
(17, 'CASE-2026-0017', 1, 'Corporate Embezzlement at Architecture Firm', 'Chief Financial Controller siphoned project retainer fees to offshore accounts.', 'Fraud', 'Under Investigation', 'High', '330 N Wabash Ave, Chicago, IL', '2026-03-04 15:30:00', NULL, 3, TRUE),
(18, 'CASE-2026-0018', 18, 'Art Gallery Burglary & Grand Larceny', 'Rare oil paintings removed from gallery during power outage.', 'Burglary', 'Under Investigation', 'High', '700 N Franklin St, Chicago, IL', '2026-03-08 02:45:00', NULL, 4, TRUE),
(19, 'CASE-2026-0019', 19, 'Residential Strongarm Robbery in Foyer', 'Resident attacked and robbed of valuables inside secure condo vestibule.', 'Robbery', 'Under Investigation', 'High', '600 W Diversey Pkwy, Chicago, IL', '2026-03-12 21:20:00', NULL, 2, TRUE),
(20, 'CASE-2026-0020', 1, 'Automobile Part Thefts (Catalytic Converters)', 'Fleet of commercial delivery vans stripped of catalytic converters overnight.', 'Theft', 'Closed', 'Low', '1200 S Canal St, Chicago, IL', '2026-03-15 05:00:00', '2026-03-29 12:00:00', 2, TRUE),
(21, 'CASE-2026-0021', 1, 'Attempted Wire Fraud at Escrow Agency', 'Business email compromise targeting property purchase closing funds.', 'Fraud', 'Closed', 'Medium', '10 S LaSalle St, Chicago, IL', '2026-03-18 11:15:00', '2026-04-02 16:45:00', 3, TRUE),
(22, 'CASE-2026-0022', 18, 'Aggravated Assault with Motor Vehicle', 'Driver deliberately struck pedestrian following traffic dispute.', 'Assault', 'Under Investigation', 'High', '100 E Ohio St, Chicago, IL', '2026-03-21 17:50:00', NULL, 4, TRUE),
(23, 'CASE-2026-0023', 2, 'Illegal Firearms Discharge near Community Park', 'Multiple rounds fired into unoccupied building from passing vehicle.', 'Other', 'Cold Case', 'Medium', '4800 S State St, Chicago, IL', '2026-03-24 23:10:00', NULL, 2, TRUE),
(24, 'CASE-2026-0024', 19, 'Bicycle Theft Ring operating on Lakefront Trail', 'Dozens of high-value racing bicycles stolen using hydraulic bolt cutters.', 'Theft', 'Pending Review', 'Low', '3100 N Lake Shore Dr, Chicago, IL', '2026-03-28 14:00:00', NULL, 2, TRUE),
(25, 'CASE-2026-0025', 1, 'Pharmacy Armed Robbery & Prescription Theft', 'Two suspects vaulted counter demanding controlled pharmaceutical narcotics.', 'Robbery', 'Under Investigation', 'Critical', '600 S Michigan Ave, Chicago, IL', '2026-04-01 19:30:00', NULL, 3, TRUE),
(26, 'CASE-2026-0026', 1, 'ATM Skimming and Debit Card Cloning', 'Skimmer and pinhole camera discovered mounted on high-traffic bank vestibule ATM.', 'Fraud', 'Under Investigation', 'Medium', '200 W Adams St, Chicago, IL', '2026-04-05 09:20:00', NULL, 2, TRUE),
(27, 'CASE-2026-0027', 18, 'Apartment Burglary via Fire Escape', 'Window forced open from third-floor fire escape platform.', 'Burglary', 'Under Investigation', 'Medium', '1200 N LaSalle Dr, Chicago, IL', '2026-04-08 19:00:00', NULL, 4, TRUE),
(28, 'CASE-2026-0028', 1, 'Disturbance and Simple Battery at Transit Hub', 'Commuter struck by disorderly subject during morning rush hour.', 'Assault', 'Closed', 'Low', '500 W Jackson Blvd, Chicago, IL', '2026-04-12 08:15:00', '2026-04-20 15:00:00', 3, TRUE),
(29, 'CASE-2026-0029', 11, 'Illicit Narcotics Operation in Vacant Property', 'Surveillance confirmed distribution of synthetic opioids from boarded structure.', 'Narcotics', 'Under Investigation', 'High', '3800 W Madison St, Chicago, IL', '2026-04-15 22:00:00', NULL, 2, TRUE),
(30, 'CASE-2026-0030', 1, 'Theft of Construction Equipment from Jobsite', 'Skid steer and power generators removed during weekend shutdown.', 'Theft', 'Open', 'Low', '400 S Wacker Dr, Chicago, IL', '2026-04-19 06:45:00', NULL, 2, TRUE),
(31, 'CASE-2026-0031', 1, 'Distributed Denial of Service on Port Authority', 'Critical logistics tracking website brought down by foreign botnet.', 'Cybercrime', 'Under Investigation', 'High', '111 E Wacker Dr, Chicago, IL', '2026-04-23 13:30:00', NULL, 3, TRUE),
(32, 'CASE-2026-0032', 18, 'Jewelry Store Smash and Grab Robbery', 'Hammers used to shatter storefront vitrines during evening shopping hours.', 'Robbery', 'Under Investigation', 'Critical', '840 N Michigan Ave, Chicago, IL', '2026-04-27 18:40:00', NULL, 4, TRUE),
(33, 'CASE-2026-0033', 19, 'Stolen Vehicle Tracking & Recovery Operation', 'Commercial vehicle reported stolen located via GPS tracking transponder.', 'Theft', 'Closed', 'Medium', '3000 N Ashland Ave, Chicago, IL', '2026-05-01 10:15:00', '2026-05-04 14:00:00', 2, TRUE),
(34, 'CASE-2026-0034', 3, 'Suspicious Death Investigation on E 75th', 'Deceased individual discovered in residential apartment with trauma.', 'Homicide', 'Under Investigation', 'Critical', '1500 E 75th St, Chicago, IL', '2026-05-05 16:50:00', NULL, 2, TRUE),
(35, 'CASE-2026-0035', 1, 'Counterfeit Luxury Goods Seizure', 'Wholesale warehouse supplying fake designer watches and accessories raided.', 'Fraud', 'Pending Review', 'Medium', '700 S Clinton St, Chicago, IL', '2026-05-09 11:00:00', NULL, 3, TRUE),
(36, 'CASE-2026-0036', 1, 'Aggravated Assault on Public Official', 'City building inspector threatened with firearm during code enforcement visit.', 'Assault', 'Under Investigation', 'High', '120 N Racine Ave, Chicago, IL', '2026-05-13 14:30:00', NULL, 2, TRUE),
(37, 'CASE-2026-0037', 18, 'Subterranean Cable Theft and Infrastructure Cut', 'Copper utility cables severed, causing localized communications blackout.', 'Theft', 'Cold Case', 'Medium', '500 N Kingsbury St, Chicago, IL', '2026-05-17 03:20:00', NULL, 4, TRUE),
(38, 'CASE-2026-0038', 19, 'Commercial Safe Cracking at Nightclub', 'Office safe drilled and emptied of weekend receipts.', 'Burglary', 'Under Investigation', 'High', '3400 N Sheffield Ave, Chicago, IL', '2026-05-21 04:10:00', NULL, 2, TRUE),
(39, 'CASE-2026-0039', 1, 'Public Transit Fare Card Counterfeiting Ring', 'Digital fraud syndicate programming illicit magnetic fare cards.', 'Cybercrime', 'Closed', 'Low', '567 W Lake St, Chicago, IL', '2026-05-25 15:45:00', '2026-06-15 11:00:00', 3, TRUE),
(40, 'CASE-2026-0040', 2, 'Street Robbery Targeting Delivery Courier', 'Driver assaulted and packages stolen from delivery van.', 'Robbery', 'Under Investigation', 'High', '5300 S Martin Luther King Jr Dr, Chicago, IL', '2026-05-29 19:15:00', NULL, 2, TRUE),
(41, 'CASE-2026-0041', 1, 'Commercial Bribery in Municipal Contract Bid', 'Subcontractor paid kickbacks to secure civil engineering contracts.', 'Fraud', 'Under Investigation', 'Medium', '121 N LaSalle St, Chicago, IL', '2026-06-02 10:30:00', NULL, 3, TRUE),
(42, 'CASE-2026-0042', 18, 'Hotel Penthouse Jewel Heist', 'High-value gems stolen from guest safe during private cocktail reception.', 'Theft', 'Under Investigation', 'High', '108 E Superior St, Chicago, IL', '2026-06-06 22:45:00', NULL, 4, TRUE),
(43, 'CASE-2026-0043', 19, 'Assault with Dangerous Instrument in Park', 'Victim struck with blunt object during dispute at recreational dog park.', 'Assault', 'Closed', 'Medium', '3800 N Recreation Dr, Chicago, IL', '2026-06-10 18:00:00', '2026-06-25 16:30:00', 2, TRUE),
(44, 'CASE-2026-0044', 1, 'Illegal Distribution of Unregistered Firearms', 'Undercover buy operation targeting straw purchaser of handguns.', 'Other', 'Pending Review', 'Critical', '2100 S Wabash Ave, Chicago, IL', '2026-06-14 20:10:00', NULL, 2, TRUE),
(45, 'CASE-2026-0045', 1, 'Hospital Network Phishing Security Breach', 'Phishing emails compromised hospital workstation credentials.', 'Cybercrime', 'Under Investigation', 'High', '251 E Huron St, Chicago, IL', '2026-06-18 11:25:00', NULL, 3, TRUE),
(46, 'CASE-2026-0046', 11, 'Warehouse Narcotics Processing Laboratory', 'Chemical synthesis equipment and precursor agents recovered.', 'Narcotics', 'Under Investigation', 'Critical', '4200 W Kinzie St, Chicago, IL', '2026-06-22 01:40:00', NULL, 2, TRUE),
(47, 'CASE-2026-0047', 18, 'Valet Parking Vehicle Theft Operation', 'Valet lockbox compromised and three luxury sports cars stolen.', 'Theft', 'Closed', 'Medium', '60 E Ontario St, Chicago, IL', '2026-06-26 23:30:00', '2026-07-08 14:00:00', 4, TRUE),
(48, 'CASE-2026-0048', 19, 'Residential Arson Investigation', 'Accelerant patterns detected in basement stairway following structural fire.', 'Other', 'Under Investigation', 'Critical', '3700 N Southport Ave, Chicago, IL', '2026-06-30 03:15:00', NULL, 2, TRUE),
(49, 'CASE-2026-0049', 1, 'Robbery of Armored Cash Transit Messenger', 'Guards ambushed while servicing commercial bank depository.', 'Robbery', 'Under Investigation', 'Critical', '230 S Clark St, Chicago, IL', '2026-07-04 13:20:00', NULL, 2, TRUE),
(50, 'CASE-2026-0050', 1, 'Industrial Intellectual Property Theft', 'Proprietary robotics source code downloaded to unauthorized external drives.', 'Cybercrime', 'Open', 'High', '600 W Chicago Ave, Chicago, IL', '2026-07-08 17:00:00', NULL, 3, TRUE)
ON DUPLICATE KEY UPDATE title = VALUES(title);

-- 4. SEED CASE ASSIGNMENTS (Respects single active lead & lifecycle dates)
INSERT INTO case_assignments (assignment_id, case_id, user_id, assignment_role, assigned_date, unassigned_date, is_active, notes) VALUES
(1, 1, 5, 'Lead Investigator', '2026-01-05 08:00:00', NULL, TRUE, 'Assigned primary investigation duties.'),
(2, 1, 2, 'Assisting Officer', '2026-01-05 08:30:00', NULL, TRUE, 'Patrol canvas and initial report intake.'),
(3, 2, 6, 'Lead Investigator', '2026-01-08 15:00:00', NULL, TRUE, 'Bank surveillance review and ballistics coordination.'),
(4, 2, 3, 'Assisting Officer', '2026-01-08 15:30:00', NULL, TRUE, 'Witness interviewing.'),
(5, 3, 5, 'Lead Investigator', '2026-01-10 13:00:00', '2026-02-15 16:30:00', FALSE, 'Financial forensics completed. Case successfully closed.'),
(6, 4, 7, 'Lead Investigator', '2026-01-15 09:00:00', NULL, TRUE, 'Riverfront security coordination.'),
(7, 5, 6, 'Lead Investigator', '2026-01-18 10:00:00', '2026-02-02 09:00:00', FALSE, 'Vehicle recovered in storage locker. Case resolved.'),
(8, 7, 5, 'Lead Investigator', '2026-01-25 10:00:00', NULL, TRUE, 'Cyber forensics examining server memory dumps.'),
(9, 8, 6, 'Lead Investigator', '2026-02-01 20:00:00', NULL, TRUE, 'DEA joint task force liaison.'),
(10, 9, 5, 'Lead Investigator', '2026-02-06 08:00:00', NULL, TRUE, 'Area homicide task force activated.'),
(11, 11, 7, 'Lead Investigator', '2026-02-13 09:00:00', NULL, TRUE, 'Automated license plate reader tracking initiated.'),
(12, 15, 5, 'Lead Investigator', '2026-02-25 11:00:00', NULL, TRUE, 'Access log review with hospital IT staff.')
ON DUPLICATE KEY UPDATE notes = VALUES(notes);

-- 5. SEED CASE PERSONS (M:N Associative Links)
INSERT INTO case_persons (case_person_id, case_id, person_id, role_in_case, statement_summary) VALUES
(1, 1, 1, 'Suspect', 'Matched surveillance clothing description. Denied presence at scene.'),
(2, 1, 2, 'Victim', 'Store manager reporting inventory losses and damaged entry doors.'),
(3, 1, 3, 'Witness', 'Night security guard who called 911 upon hearing glass break.'),
(4, 2, 4, 'Suspect', 'Identified by branch teller from photographic array.'),
(5, 2, 5, 'Victim', 'Bank teller who received weapon threat.'),
(6, 4, 7, 'Suspect', 'Apprehended two blocks south of scene with knife.'),
(7, 4, 8, 'Victim', 'Treated by EMS at scene for lacerations.'),
(8, 4, 9, 'Witness', 'Bystander providing smartphone video recording of altercation.'),
(9, 9, 11, 'Suspect', 'Vehicle registered to suspect observed leaving scene at high speed.'),
(10, 9, 12, 'Victim', 'Deceased victim identified by family.'),
(11, 9, 13, 'Witness', 'Heard three gunshots and observed dark sedan fleeing southbound.')
ON DUPLICATE KEY UPDATE statement_summary = VALUES(statement_summary);

-- 6. SEED EVIDENCE ITEMS (Chain of Custody Initial State)
INSERT INTO evidence (evidence_id, case_id, evidence_code, evidence_type, description, current_storage_location, current_custody_status, collected_date, collected_by) VALUES
(1, 1, 'EVID-2026-0001-A', 'Physical', 'Heavy steel prybar recovered near rear door point of entry', 'Vault Locker B-12', 'Vault Storage', '2026-01-05 03:45:00', 2),
(2, 1, 'EVID-2026-0001-B', 'Digital', 'Security NVR USB export containing 4 hours of high-res surveillance footage', 'Digital Forensics Lab', 'In Analysis', '2026-01-05 04:30:00', 5),
(3, 2, 'EVID-2026-0002-A', 'Documentary', 'Handwritten demand note on yellow lined paper: "Cash in bag, no alarms"', 'Vault Locker B-14', 'Vault Storage', '2026-01-08 14:40:00', 6),
(4, 2, 'EVID-2026-0002-B', 'Forensic', 'Latent fingerprint lift lifted from teller counter acrylic partition', 'State Police Forensics Lab', 'In Analysis', '2026-01-08 16:15:00', 6),
(5, 4, 'EVID-2026-0004-A', 'Weapons', 'Folding tactical knife with 3.5-inch serrated blade and trace DNA', 'State Police Forensics Lab', 'In Analysis', '2026-01-15 00:30:00', 4),
(6, 7, 'EVID-2026-0007-A', 'Digital', 'Server hard drive image containing ransom note binary and payload script', 'Digital Forensics Lab', 'In Analysis', '2026-01-25 11:20:00', 5),
(7, 9, 'EVID-2026-0009-A', 'Forensic', 'Three spent 9mm shell casings recovered from pavement', 'Ballistics Division Vault', 'Vault Storage', '2026-02-05 22:30:00', 2)
ON DUPLICATE KEY UPDATE description = VALUES(description);

-- 7. SEED SUBSEQUENT CHAIN-OF-CUSTODY TRANSFER EVENTS
-- (Note: Initial collection records are generated automatically by trg_evidence_initial_custody)
-- The records below demonstrate historical transfers and location updates without hardcoding custody_id:
INSERT INTO evidence_custody_log (evidence_id, previous_status, new_status, from_location, to_location, handled_by, reason_for_transfer, logged_at) VALUES
(1, 'Collected', 'Vault Storage', 'Squad Car 101 Transport', 'Vault Locker B-12', 2, 'Transferred to secure station locker after intake booking', '2026-01-05 06:00:00'),
(2, 'Collected', 'In Analysis', 'Scene / Origin of Discovery', 'Digital Forensics Lab', 5, 'Transferred for cyber evidence extraction and forensic imaging', '2026-01-05 08:30:00'),
(4, 'Collected', 'In Analysis', 'Vault Locker B-14', 'State Police Forensics Lab', 6, 'Transferred for latent fingerprint comparison', '2026-01-09 10:15:00'),
(5, 'Collected', 'In Analysis', 'Scene / Origin of Discovery', 'State Police Forensics Lab', 4, 'Transferred for knife blade toolmark and DNA recovery', '2026-01-15 08:00:00');

-- 8. SEED INVESTIGATION DIARY NOTES
INSERT INTO investigation_notes (note_id, case_id, author_id, note_title, note_body, is_confidential, logged_at) VALUES
(1, 1, 5, 'Surveillance Video Initial Review', 'Reviewed retail store surveillance cameras. Two masked individuals entered at 02:22 AM. Suspect 1 matches height of Sterling.', FALSE, '2026-01-06 09:30:00'),
(2, 1, 5, 'Confidential Informant Contact', 'Confidential informant indicates stolen luxury items were offered for bulk sale in south suburbs.', TRUE, '2026-01-07 14:15:00'),
(3, 2, 6, 'Bank Staff Debriefing', 'Interviewed teller. Suspect spoke with slight rasp and wore dark reflective sunglasses.', FALSE, '2026-01-08 17:00:00'),
(4, 7, 5, 'Ransomware Bitcoin Wallet Tracing', 'Wallet address in ransom note linked to previous European financial sector extortion campaigns.', TRUE, '2026-01-26 15:45:00'),
(5, 9, 5, 'Canvass of Adjacent Commercial Properties', 'Gas station across street has exterior camera that may have captured license plate of fleeing sedan.', FALSE, '2026-02-06 11:20:00')
ON DUPLICATE KEY UPDATE note_title = VALUES(note_title);
