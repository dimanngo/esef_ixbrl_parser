import sys
import os
from arelle import Cntlr
from arelle.ModelXbrl import ModelXbrl
from arelle import ModelManager

class ArelleESEFValidator:
    def __init__(self, file_path):
        self.file_path = file_path
        self.cntlr = Cntlr.Cntlr(logFileName="logfile.txt")
        self.cntlr.startLogging(logFileName="logfile.txt")
        self.modelManager = ModelManager.initialize(self.cntlr)

    def validate(self):
        # Load the instance document
        modelXbrl = self.modelManager.load(self.file_path)

        if modelXbrl.modelDocument is None:
            print("Unable to load the instance document.")
            return

        # Perform validation
        modelXbrl.modelManager.validateInferenceRules()

        # Get validation results
        validation_results = []
        for xbrlError in modelXbrl.errors:
            code, level, message = xbrlError
            validation_results.append({
                'code': code,
                'level': level,
                'message': message
            })

        # Close the model to free up resources
        self.modelManager.close()

        return validation_results

    def validate_esef_rules(self):
        # Load ESEF rules
        rules_file = "path_to_esef_rules.json"  # You need to provide the ESEF rules file
        self.cntlr.webCache.normalizeUrl(rules_file)
        
        modelXbrl = self.modelManager.load(self.file_path)
        
        # Validate against ESEF rules
        from arelle.plugin.validate.EFM import validateEFM
        validateEFM(modelXbrl)
        
        # Get ESEF-specific validation results
        esef_results = []
        for xbrlError in modelXbrl.errors:
            if xbrlError[0].startswith("ESEF."):
                code, level, message = xbrlError
                esef_results.append({
                    'code': code,
                    'level': level,
                    'message': message
                })
        
        self.modelManager.close()
        
        return esef_results

# Usage
validator = ArelleESEFValidator('sample_esef.xhtml')

print("General XBRL Validation Results:")
results = validator.validate()
for result in results:
    print(f"Code: {result['code']}, Level: {result['level']}, Message: {result['message']}")

print("\nESEF-specific Validation Results:")
esef_results = validator.validate_esef_rules()
for result in esef_results:
    print(f"Code: {result['code']}, Level: {result['level']}, Message: {result['message']}")