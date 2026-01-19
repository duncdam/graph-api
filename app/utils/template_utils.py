from jinja2 import Environment, FileSystemLoader, Template
from pathlib import Path
import os


class CypherTemplateManager:
    """Manages Cypher query templates using Jinja2."""

    def __init__(self, template_dir: str = None):
        if template_dir is None:
            template_dir = Path(__file__).parent.parent / "templates"

        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(parents=True, exist_ok=True)

        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render_template(self, template_name: str, **kwargs) -> str:
        """
        Render a Cypher template with the given parameters.

        Args:
            template_name: Name of the template file (e.g., 'get_patient_medications.cypher')
            **kwargs: Template variables

        Returns:
            Rendered Cypher query string
        """
        template = self.env.get_template(template_name)
        return template.render(**kwargs)

    def render_from_string(self, template_string: str, **kwargs) -> str:
        """
        Render a Cypher template from a string.

        Args:
            template_string: Template string
            **kwargs: Template variables

        Returns:
            Rendered Cypher query string
        """
        template = Template(template_string)
        return template.render(**kwargs)


# Global instance
cypher_template_manager = CypherTemplateManager()
