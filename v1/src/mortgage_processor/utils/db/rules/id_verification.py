"""
Identity Document Verification Rules

Comprehensive rules for verifying identity documents in mortgage processing.
All rules are stored as Neo4j nodes to maintain the 100% data-driven approach.

Categories:
- Driver's License Verification (15 rules)
- Passport Verification (10 rules)  
- State ID Verification (10 rules)
- SSN Verification (5 rules)
- Enhanced cross-document validation
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


def load_id_verification_rules(connection):
    """Load comprehensive identity verification rules into Neo4j."""
    
    id_verification_rules = [
        
        # ===== DRIVER'S LICENSE RULES (15 rules) =====
        {
            "rule_id": "DL_001_BASIC_VALIDITY",
            "category": "DriversLicense", 
            "document_type": "drivers_license",
            "required_count": 1,
            "validation_criteria": ["not_expired", "state_issued", "photo_present", "signature_present"],
            "required_fields": ["full_name", "date_of_birth", "address", "license_number", "expiration_date", "issue_date", "state"],
            "red_flags": ["expired", "damaged", "altered", "photo_mismatch", "signature_missing"],
            "expiration_tolerance_days": 30,
            "description": "Basic driver's license validity verification"
        },
        {
            "rule_id": "DL_002_NAME_CONSISTENCY",
            "category": "DriversLicense",
            "document_type": "drivers_license", 
            "validation_criteria": ["exact_name_match", "acceptable_variations", "middle_initial_flexible"],
            "required_fields": ["full_name", "first_name", "last_name"],
            "red_flags": ["name_mismatch", "gender_inconsistent", "suspicious_alterations"],
            "name_matching_tolerance": "fuzzy_80_percent",
            "description": "Name consistency verification across mortgage documents"
        },
        {
            "rule_id": "DL_003_ADDRESS_VERIFICATION",
            "category": "DriversLicense",
            "document_type": "drivers_license",
            "validation_criteria": ["current_address", "address_format_valid", "state_residency"],
            "required_fields": ["address", "city", "state", "zip_code"],
            "red_flags": ["po_box_only", "temporary_address", "out_of_state_inconsistent"],
            "address_staleness_months": 24,
            "description": "Address verification and residency confirmation"
        },
        {
            "rule_id": "DL_004_AGE_VERIFICATION",
            "category": "DriversLicense", 
            "document_type": "drivers_license",
            "validation_criteria": ["age_calculation_accurate", "minimum_age_18", "reasonable_age_range"],
            "required_fields": ["date_of_birth"],
            "red_flags": ["age_under_18", "age_over_100", "future_birth_date", "invalid_date_format"],
            "minimum_age": 18,
            "maximum_age": 100,
            "description": "Age verification for mortgage eligibility"
        },
        {
            "rule_id": "DL_005_LICENSE_CLASS_VALIDATION",
            "category": "DriversLicense",
            "document_type": "drivers_license", 
            "validation_criteria": ["valid_license_class", "appropriate_restrictions", "commercial_vs_regular"],
            "required_fields": ["license_class", "restrictions"],
            "acceptable_classes": ["Class C", "Class D", "Class M", "CDL A", "CDL B"],
            "description": "License class and restriction validation"
        },
        {
            "rule_id": "DL_006_SECURITY_FEATURES",
            "category": "DriversLicense",
            "document_type": "drivers_license",
            "validation_criteria": ["security_features_present", "hologram_visible", "raised_text", "microprint"],
            "required_fields": ["state_seal", "security_features"],
            "red_flags": ["missing_security_features", "poor_print_quality", "suspicious_materials"],
            "description": "Security features verification for fraud prevention"
        },
        {
            "rule_id": "DL_007_STATE_FORMAT_COMPLIANCE",
            "category": "DriversLicense", 
            "document_type": "drivers_license",
            "validation_criteria": ["state_format_correct", "license_number_format", "layout_authentic"],
            "required_fields": ["state", "license_number"],
            "red_flags": ["invalid_format", "non_standard_layout", "incorrect_fonts"],
            "description": "State-specific format and layout verification"
        },
        {
            "rule_id": "DL_008_PHOTO_VALIDATION",
            "category": "DriversLicense",
            "document_type": "drivers_license", 
            "validation_criteria": ["photo_quality", "face_visible", "appropriate_background", "recent_photo"],
            "required_fields": ["photo"],
            "red_flags": ["no_photo", "obscured_face", "inappropriate_photo", "photo_altered"],
            "photo_age_limit_years": 8,
            "description": "Photo quality and authenticity verification"
        },
        {
            "rule_id": "DL_009_DUPLICATE_DETECTION",
            "category": "DriversLicense",
            "document_type": "drivers_license",
            "validation_criteria": ["unique_license_number", "no_duplicates_system", "cross_reference_check"],
            "required_fields": ["license_number", "state"],
            "red_flags": ["duplicate_license_number", "multiple_states", "fraudulent_duplicate"],
            "description": "Duplicate license detection and prevention"
        },
        {
            "rule_id": "DL_010_ENDORSEMENT_VERIFICATION",
            "category": "DriversLicense",
            "document_type": "drivers_license",
            "validation_criteria": ["valid_endorsements", "endorsement_consistency", "special_permits"],
            "required_fields": ["endorsements"],
            "acceptable_endorsements": ["motorcycle", "school_bus", "passenger", "hazmat"],
            "description": "License endorsements and special permits verification"
        },
        {
            "rule_id": "DL_011_RENEWAL_HISTORY",
            "category": "DriversLicense", 
            "document_type": "drivers_license",
            "validation_criteria": ["renewal_pattern_normal", "gap_analysis", "continuous_validity"],
            "required_fields": ["issue_date", "expiration_date", "renewal_history"],
            "red_flags": ["frequent_renewals", "suspicious_gaps", "irregular_pattern"],
            "description": "License renewal history and pattern analysis"
        },
        {
            "rule_id": "DL_012_CROSS_DOCUMENT_VALIDATION",
            "category": "DriversLicense",
            "document_type": "drivers_license",
            "validation_criteria": ["matches_other_docs", "consistent_information", "no_conflicts"],
            "cross_reference_docs": ["passport", "ssn_card", "utility_bills", "pay_stubs"],
            "red_flags": ["information_conflicts", "inconsistent_data", "suspicious_discrepancies"],
            "description": "Cross-document information consistency validation"
        },
        {
            "rule_id": "DL_013_DIGITAL_VERIFICATION",
            "category": "DriversLicense",
            "document_type": "drivers_license", 
            "validation_criteria": ["digital_signature_valid", "barcode_readable", "magnetic_stripe"],
            "required_fields": ["barcode_data", "digital_signature"],
            "red_flags": ["unreadable_barcode", "invalid_digital_signature", "missing_digital_elements"],
            "description": "Digital elements and electronic verification"
        },
        {
            "rule_id": "DL_014_VETERAN_DESIGNATION",
            "category": "DriversLicense",
            "document_type": "drivers_license",
            "validation_criteria": ["veteran_status_verified", "military_service_confirmed", "designation_authentic"],
            "optional_fields": ["veteran_designation", "military_service_info"],
            "description": "Veteran designation verification for VA loans"
        },
        {
            "rule_id": "DL_015_ORGAN_DONOR_STATUS",
            "category": "DriversLicense", 
            "document_type": "drivers_license",
            "validation_criteria": ["donor_status_clear", "consent_documented"],
            "optional_fields": ["organ_donor_status"],
            "description": "Organ donor status verification (informational)"
        },

        # ===== PASSPORT RULES (10 rules) =====
        {
            "rule_id": "PP_001_BASIC_VALIDITY",
            "category": "Passport",
            "document_type": "passport",
            "required_count": 1,
            "validation_criteria": ["not_expired", "government_issued", "photo_present", "signature_present"],
            "required_fields": ["full_name", "date_of_birth", "passport_number", "country_of_issue", "expiration_date", "issue_date"],
            "red_flags": ["expired", "damaged", "altered", "photo_mismatch", "signature_missing"],
            "expiration_tolerance_days": 180,
            "description": "Basic passport validity verification"
        },
        {
            "rule_id": "PP_002_CITIZENSHIP_VERIFICATION",
            "category": "Passport", 
            "document_type": "passport",
            "validation_criteria": ["citizenship_confirmed", "country_valid", "birth_place_consistent"],
            "required_fields": ["country_of_citizenship", "place_of_birth"],
            "red_flags": ["citizenship_questions", "conflicting_information", "suspicious_origins"],
            "description": "Citizenship and country of origin verification"
        },
        {
            "rule_id": "PP_003_VISA_STATUS_CHECK",
            "category": "Passport",
            "document_type": "passport", 
            "validation_criteria": ["visa_status_appropriate", "work_authorization", "residency_status"],
            "required_fields": ["visa_pages", "immigration_stamps"],
            "red_flags": ["expired_visa", "unauthorized_work", "overstay_indicators"],
            "description": "Visa and immigration status verification"
        },
        {
            "rule_id": "PP_004_BIOMETRIC_DATA",
            "category": "Passport",
            "document_type": "passport",
            "validation_criteria": ["biometric_chip_present", "chip_data_readable", "digital_photo_match"],
            "required_fields": ["biometric_chip", "digital_photo"],
            "red_flags": ["damaged_chip", "unreadable_data", "biometric_mismatch"],
            "description": "Biometric data and chip verification"
        },
        {
            "rule_id": "PP_005_SECURITY_FEATURES",
            "category": "Passport", 
            "document_type": "passport",
            "validation_criteria": ["security_features_authentic", "watermarks_present", "special_inks"],
            "required_fields": ["security_features", "watermarks"],
            "red_flags": ["missing_security_features", "fake_watermarks", "poor_security_printing"],
            "description": "Passport security features verification"
        },
        {
            "rule_id": "PP_006_TRAVEL_HISTORY",
            "category": "Passport",
            "document_type": "passport",
            "validation_criteria": ["travel_pattern_reasonable", "entry_exit_consistent", "stamp_authenticity"],
            "required_fields": ["immigration_stamps", "travel_history"],
            "red_flags": ["suspicious_travel_patterns", "fake_stamps", "irregular_entries"],
            "description": "Travel history and immigration stamp verification"
        },
        {
            "rule_id": "PP_007_NAME_TRANSLITERATION", 
            "category": "Passport",
            "document_type": "passport",
            "validation_criteria": ["name_transliteration_consistent", "character_accuracy", "spelling_variations"],
            "required_fields": ["full_name", "name_in_native_script"],
            "red_flags": ["inconsistent_transliteration", "character_errors", "suspicious_variations"],
            "description": "Name transliteration and character consistency"
        },
        {
            "rule_id": "PP_008_RENEWAL_PATTERN",
            "category": "Passport",
            "document_type": "passport",
            "validation_criteria": ["renewal_pattern_normal", "previous_passport_info", "continuous_citizenship"],
            "required_fields": ["previous_passport_number", "renewal_date"],
            "red_flags": ["frequent_renewals", "citizenship_changes", "suspicious_renewal_pattern"],
            "description": "Passport renewal history and pattern analysis"
        },
        {
            "rule_id": "PP_009_EMERGENCY_PASSPORT",
            "category": "Passport", 
            "document_type": "passport",
            "validation_criteria": ["emergency_status_documented", "valid_circumstances", "temporary_nature"],
            "optional_fields": ["emergency_designation", "circumstances"],
            "red_flags": ["frequent_emergency_passports", "suspicious_circumstances"],
            "description": "Emergency passport verification and validation"
        },
        {
            "rule_id": "PP_010_DIPLOMATIC_STATUS",
            "category": "Passport",
            "document_type": "passport",
            "validation_criteria": ["diplomatic_status_verified", "official_capacity", "government_confirmation"],
            "optional_fields": ["diplomatic_designation", "official_status"],
            "description": "Diplomatic and official passport verification"
        },

        # ===== STATE ID RULES (10 rules) =====
        {
            "rule_id": "SID_001_BASIC_VALIDITY",
            "category": "StateID",
            "document_type": "state_id",
            "required_count": 1, 
            "validation_criteria": ["not_expired", "state_issued", "photo_present", "valid_format"],
            "required_fields": ["full_name", "date_of_birth", "address", "id_number", "expiration_date", "issue_date", "state"],
            "red_flags": ["expired", "damaged", "altered", "photo_mismatch", "invalid_format"],
            "expiration_tolerance_days": 30,
            "description": "Basic state ID validity verification"
        },
        {
            "rule_id": "SID_002_NON_DRIVER_VERIFICATION",
            "category": "StateID",
            "document_type": "state_id",
            "validation_criteria": ["non_driver_status_clear", "age_appropriate", "disability_considerations"],
            "required_fields": ["non_driver_designation"],
            "red_flags": ["conflicting_driver_status", "age_inconsistency"],
            "description": "Non-driver status and circumstances verification"
        },
        {
            "rule_id": "SID_003_REAL_ID_COMPLIANCE",
            "category": "StateID", 
            "document_type": "state_id",
            "validation_criteria": ["real_id_compliant", "gold_star_present", "enhanced_security"],
            "required_fields": ["real_id_designation", "security_features"],
            "red_flags": ["non_compliant_id", "missing_real_id_features"],
            "description": "REAL ID Act compliance verification"
        },
        {
            "rule_id": "SID_004_ADDRESS_CONSISTENCY",
            "category": "StateID",
            "document_type": "state_id",
            "validation_criteria": ["address_current", "residency_confirmed", "utility_bills_match"],
            "required_fields": ["address", "city", "state", "zip_code"],
            "cross_reference_docs": ["utility_bills", "bank_statements", "lease_agreement"],
            "red_flags": ["address_mismatch", "temporary_address", "po_box_only"],
            "description": "Address consistency and residency verification"
        },
        {
            "rule_id": "SID_005_AGE_VERIFICATION_ENHANCED",
            "category": "StateID",
            "document_type": "state_id", 
            "validation_criteria": ["age_calculation_precise", "birth_certificate_match", "reasonable_age"],
            "required_fields": ["date_of_birth"],
            "cross_reference_docs": ["birth_certificate", "passport"],
            "red_flags": ["age_inconsistency", "impossible_dates", "calculation_errors"],
            "description": "Enhanced age verification with cross-referencing"
        },
        {
            "rule_id": "SID_006_PHOTO_AUTHENTICATION",
            "category": "StateID",
            "document_type": "state_id",
            "validation_criteria": ["photo_quality_acceptable", "recent_photo", "face_recognition_compatible"],
            "required_fields": ["photo"],
            "red_flags": ["poor_photo_quality", "old_photo", "face_obscured", "photo_manipulation"],
            "photo_age_limit_years": 10,
            "description": "Photo authentication and quality verification"
        },
        {
            "rule_id": "SID_007_DUPLICATE_PREVENTION",
            "category": "StateID",
            "document_type": "state_id",
            "validation_criteria": ["unique_id_number", "no_duplicate_records", "identity_theft_check"],
            "required_fields": ["id_number", "state"],
            "red_flags": ["duplicate_id_detected", "identity_theft_indicators", "suspicious_applications"],
            "description": "Duplicate ID detection and identity theft prevention"
        },
        {
            "rule_id": "SID_008_MEDICAL_DESIGNATION",
            "category": "StateID", 
            "document_type": "state_id",
            "validation_criteria": ["medical_info_accurate", "disability_status_verified", "medical_restrictions"],
            "optional_fields": ["medical_conditions", "disability_designation"],
            "description": "Medical conditions and disability designation verification"
        },
        {
            "rule_id": "SID_009_VOTER_REGISTRATION",
            "category": "StateID",
            "document_type": "state_id",
            "validation_criteria": ["voter_status_consistent", "registration_current", "eligibility_confirmed"],
            "optional_fields": ["voter_registration_status"],
            "description": "Voter registration status verification"
        },
        {
            "rule_id": "SID_010_EMERGENCY_CONTACT",
            "category": "StateID",
            "document_type": "state_id", 
            "validation_criteria": ["emergency_contact_valid", "relationship_appropriate", "contact_reachable"],
            "optional_fields": ["emergency_contact_info"],
            "description": "Emergency contact information verification"
        },

        # ===== SSN VERIFICATION RULES (5 rules) =====
        {
            "rule_id": "SSN_001_FORMAT_VALIDATION",
            "category": "SSN",
            "document_type": "ssn_card",
            "required_count": 1,
            "validation_criteria": ["format_correct", "no_invalid_sequences", "area_number_valid"],
            "required_fields": ["ssn_number", "full_name"],
            "red_flags": ["invalid_format", "known_invalid_sequence", "fake_area_code"],
            "ssn_format_pattern": "XXX-XX-XXXX",
            "description": "SSN format and sequence validation"
        },
        {
            "rule_id": "SSN_002_NAME_CONSISTENCY",
            "category": "SSN",
            "document_type": "ssn_card",
            "validation_criteria": ["name_exact_match", "ssa_records_consistent", "no_name_changes"],
            "required_fields": ["full_name", "first_name", "last_name"],
            "cross_reference_docs": ["drivers_license", "passport", "birth_certificate"],
            "red_flags": ["name_mismatch", "suspicious_name_changes", "identity_inconsistency"],
            "description": "SSN name consistency across documents"
        },
        {
            "rule_id": "SSN_003_ISSUANCE_VERIFICATION",
            "category": "SSN", 
            "document_type": "ssn_card",
            "validation_criteria": ["issuance_date_reasonable", "age_at_issuance", "birth_state_consistency"],
            "required_fields": ["issuance_date", "date_of_birth"],
            "red_flags": ["late_issuance", "age_inconsistency", "suspicious_timing"],
            "description": "SSN issuance timing and circumstances verification"
        },
        {
            "rule_id": "SSN_004_DEATH_MASTER_FILE",
            "category": "SSN",
            "document_type": "ssn_card",
            "validation_criteria": ["not_deceased", "death_records_check", "active_status"],
            "required_fields": ["ssn_number"],
            "red_flags": ["deceased_ssn", "death_record_match", "inactive_status"],
            "description": "Death Master File verification for active status"
        },
        {
            "rule_id": "SSN_005_WORK_AUTHORIZATION",
            "category": "SSN", 
            "document_type": "ssn_card",
            "validation_criteria": ["work_authorized", "valid_for_employment", "no_restrictions"],
            "required_fields": ["work_authorization_status"],
            "red_flags": ["not_valid_for_work", "restricted_ssn", "temporary_authorization"],
            "description": "Work authorization and employment eligibility verification"
        }
    ]
    
    # Store rules in Neo4j
    with connection.driver.session(database=connection.database) as session:
        for rule in id_verification_rules:
            # Ensure all parameters are explicitly set to avoid ParameterMissing errors
            rule_params = {
                "rule_id": rule.get("rule_id"),
                "category": rule.get("category"),
                "document_type": rule.get("document_type"),
                "required_count": rule.get("required_count"),
                "time_period": rule.get("time_period"),
                "validation_criteria": rule.get("validation_criteria"),
                "required_fields": rule.get("required_fields"),
                "optional_fields": rule.get("optional_fields"),
                "red_flags": rule.get("red_flags"),
                "exceptions": rule.get("exceptions"),
                "alternative_docs": rule.get("alternative_docs"),
                "cross_reference_docs": rule.get("cross_reference_docs"),
                "expiration_tolerance_days": rule.get("expiration_tolerance_days"),
                "name_matching_tolerance": rule.get("name_matching_tolerance"),
                "address_staleness_months": rule.get("address_staleness_months"),
                "minimum_age": rule.get("minimum_age"),
                "maximum_age": rule.get("maximum_age"),
                "acceptable_classes": rule.get("acceptable_classes"),
                "acceptable_endorsements": rule.get("acceptable_endorsements"),
                "photo_age_limit_years": rule.get("photo_age_limit_years"),
                "ssn_format_pattern": rule.get("ssn_format_pattern"),
                "description": rule.get("description")
            }
            
            query = """
            CREATE (rule:IDVerificationRule {
                rule_id: $rule_id,
                category: $category,
                document_type: $document_type,
                required_count: $required_count,
                time_period: $time_period,
                validation_criteria: $validation_criteria,
                required_fields: $required_fields,
                optional_fields: $optional_fields,
                red_flags: $red_flags,
                exceptions: $exceptions,
                alternative_docs: $alternative_docs,
                cross_reference_docs: $cross_reference_docs,
                expiration_tolerance_days: $expiration_tolerance_days,
                name_matching_tolerance: $name_matching_tolerance,
                address_staleness_months: $address_staleness_months,
                minimum_age: $minimum_age,
                maximum_age: $maximum_age,
                acceptable_classes: $acceptable_classes,
                acceptable_endorsements: $acceptable_endorsements,
                photo_age_limit_years: $photo_age_limit_years,
                ssn_format_pattern: $ssn_format_pattern,
                description: $description
            })
            """
            
            session.run(query, rule_params)
        
        logger.info(f"Created {len(id_verification_rules)} ID verification rules")
        logger.info("ID verification rules categories: Driver's License (15), Passport (10), State ID (10), SSN (5)")


if __name__ == "__main__":
    # Test the rule creation
    from mortgage_processor.utils.db import get_neo4j_connection, initialize_connection
    initialize_connection()
    connection = get_neo4j_connection()
    load_id_verification_rules(connection)
