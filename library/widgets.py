from django import forms
from django.utils.safestring import mark_safe

class EditorMDWidget(forms.Textarea):
    class Media:
        css = {
            'all': (
                'editormd/css/editormd.min.css',
                'editormd/css/editormd.preview.min.css',
                'https://cdn.jsdelivr.net/npm/github-markdown-css/github-markdown.min.css',
            )
        }
        js = (
            'editormd/editormd.min.js',
            'editormd/lib/marked.min.js',
            'editormd/lib/prettify.min.js',
            'editormd/lib/raphael.min.js',
            'editormd/lib/underscore.min.js',
            'editormd/lib/sequence-diagram.min.js',
            'editormd/lib/flowchart.min.js',
            'editormd/lib/jquery.flowchart.min.js',
        )

    def render(self, name, value, attrs=None, renderer=None):
        editor_id = attrs.get('id', f'id_{name}')
        html = f"""
        <div id="{editor_id}_container" class="editor-md-container">
            <textarea style="display:none;" name="{name}" id="{editor_id}">{value or ''}</textarea>
        </div>
        <script>
        $(function() {{
            editormd("{editor_id}_container", {{
                width: "100%",
                height: 640,
                path: "/static/editormd/lib/",
                toolbar: true,
                toolbarIcons: "full",               // ✅ 完整按鈕列
                saveHTMLToTextarea: true,
                emoji: true,
                taskList: true,
                tex: true,
                flowChart: true,
                sequenceDiagram: true,
                codeFold: true,
                previewTheme: "default",
                theme: "default",
                editorTheme: "default",
                watch: true,
                highlight: true,
            }});
        }});
        </script>
        """
        return mark_safe(html)