from django import forms

from homebank.transaction_management.managers import RabobankCsvRowParser
from homebank.utils import FileValidator, csv_content_types_allowed


class CsvImportForm(forms.Form):
    csv_file = forms.FileField(validators=[FileValidator(content_types=csv_content_types_allowed)])
    parser = RabobankCsvRowParser()

    # overwrite a field: clean_<name>
    def clean_name(self):
        pass
