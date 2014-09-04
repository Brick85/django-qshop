from django.forms.widgets import ChoiceFieldRenderer, format_html, force_text, mark_safe, CheckboxChoiceInput, RendererMixin, SelectMultiple
import re

gre_get_level = re.compile("^((?:- )*).*")

class CategoryCheckboxFieldRenderer(ChoiceFieldRenderer):
    choice_input_class = CheckboxChoiceInput
    def render(self):
        id_ = self.attrs.get('id', None)
        start_tag = format_html(u'<ul class="category_ul" id="{0}">', id_) if id_ else u'<ul>'
        output = [start_tag]
        old_level = 0
        for i, choice in enumerate(self.choices):
            level_dashes = gre_get_level.findall(choice[1])[0]
            choice = (choice[0], choice[1].replace(level_dashes, ""))
            level = level_dashes.count(u"-")
            if level != old_level:
                if level > old_level:
                    for j in range(0, level-old_level):
                        output.append(u'<ul>')
                else:
                    for j in range(0, old_level-level):
                        output.append(u'</ul>')
            old_level = level
            w = self.choice_input_class(self.name, self.value, self.attrs.copy(), choice, i)
            output.append(format_html(u'<li>{0}</li>', force_text(w)))
        output.append(u'</ul>')
        return mark_safe('\n'.join(output))

class CategoryCheckboxSelectMultiple(RendererMixin, SelectMultiple):
    renderer = CategoryCheckboxFieldRenderer
    _empty_value = []
    class Media:
        css = {
            'all': ('admin/qshop/css/widget_category_select.css',)
        }
    def get_help_text(self, text):
        return "asd"
