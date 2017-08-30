from django.forms.widgets import CheckboxSelectMultiple
import re

gre_get_level = re.compile("^((?:- )*).*")

class CategoryCheckboxSelectMultiple(CheckboxSelectMultiple):
    option_template_name = 'django/forms/widgets/checkbox_option.html'

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        level_dashes = gre_get_level.findall(label)[0]
        level = level_dashes.count(u"-")        

        if level:
            attrs["style"] = "margin-left: {}px".format(level*30)
            label=label.replace(level_dashes, "")
        else:
            attrs["style"] = ""

        return super(CategoryCheckboxSelectMultiple, self).create_option(name, value, label, selected, index, subindex, attrs)
