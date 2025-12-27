"""
CLI interface using Click framework
Provides commands for running and managing debates
"""
import click
import asyncio
import os
from src.models import DebateTopic, AgentConfig
from src.orchestrator import DebateOrchestrator
from src.utils import format_debate_for_display, format_debate_as_markdown, format_debates_list
from src.exceptions import DebateNotFoundError


@click.group()
def cli_group():
    """Multi-agent debate system CLI"""
    pass


@cli_group.command(name='debate')
@click.option('--topic', required=True, help='Debate topic title')
@click.option('--description', required=True, help='Debate topic description')
@click.option('--provider', default='claude', type=click.Choice(['claude', 'gemini', 'mixed']), help='AI provider: claude, gemini, or mixed')
@click.option('--output', default=None, help='Output file for debate results (optional)')
def debate_command(topic, description, provider, output):
    """Run a debate on the given topic"""
    click.echo(f"\n🔄 Starting debate: {topic}")
    click.echo(f"   Description: {description}")
    click.echo(f"   Provider: {provider}\n")

    try:
        # Create topic
        debate_topic = DebateTopic(
            title=topic,
            description=description
        )

        # Define agents based on selected provider
        if provider == 'claude':
            agents_config = [
                AgentConfig(
                    name="Claude FOR",
                    role="FOR",
                    model_provider="claude",
                    model_name="haiku"
                ),
                AgentConfig(
                    name="Claude AGAINST",
                    role="AGAINST",
                    model_provider="claude",
                    model_name="haiku"
                ),
                AgentConfig(
                    name="Claude SYNTHESIS",
                    role="SYNTHESIS",
                    model_provider="claude",
                    model_name="haiku"
                ),
            ]
        elif provider == 'gemini':
            agents_config = [
                AgentConfig(
                    name="Gemini FOR",
                    role="FOR",
                    model_provider="gemini",
                    model_name="flash"
                ),
                AgentConfig(
                    name="Gemini AGAINST",
                    role="AGAINST",
                    model_provider="gemini",
                    model_name="flash"
                ),
                AgentConfig(
                    name="Gemini SYNTHESIS",
                    role="SYNTHESIS",
                    model_provider="gemini",
                    model_name="flash"
                ),
            ]
        else:  # mixed
            agents_config = [
                AgentConfig(
                    name="Claude FOR",
                    role="FOR",
                    model_provider="claude",
                    model_name="haiku"
                ),
                AgentConfig(
                    name="Gemini AGAINST",
                    role="AGAINST",
                    model_provider="gemini",
                    model_name="flash"
                ),
                AgentConfig(
                    name="Claude SYNTHESIS",
                    role="SYNTHESIS",
                    model_provider="claude",
                    model_name="haiku"
                ),
            ]

        # Run debate
        orchestrator = DebateOrchestrator()
        debate = asyncio.run(orchestrator.run_debate(debate_topic, agents_config))

        # Format and display results
        debate_output = format_debate_for_display(debate)
        click.echo(debate_output)

        # Save to file if requested
        if output:
            with open(output, 'w') as f:
                f.write(debate_output)
            click.echo(f"\n✅ Debate saved to {output}")

        # Always show debate ID
        click.echo(f"\n📋 Debate ID: {debate.debate_id}")
        click.echo("   Use this ID to view or export the debate later")

    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        raise click.ClickException(str(e))


@cli_group.group(name='debates')
def debates_group():
    """Manage stored debates"""
    pass


@debates_group.command(name='list')
@click.option('--limit', default=10, type=int, help='Maximum debates to list')
def debates_list_command(limit):
    """List stored debates"""
    try:
        orchestrator = DebateOrchestrator()
        debates = orchestrator.list_debates(limit=limit)

        if debates:
            click.echo("\n" + format_debates_list(debates))
        else:
            click.echo("\n✨ No debates stored yet. Run one with: debate --topic ... --description ...")

    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        raise click.ClickException(str(e))


@debates_group.command(name='view')
@click.argument('debate_id')
@click.option('--format', 'output_format', default='text', type=click.Choice(['text', 'markdown']), help='Output format')
def debates_view_command(debate_id, output_format):
    """View a specific debate"""
    try:
        orchestrator = DebateOrchestrator()
        debate = orchestrator.get_debate(debate_id)

        if output_format == 'markdown':
            output = format_debate_as_markdown(debate)
        else:
            output = format_debate_for_display(debate)

        click.echo("\n" + output)

    except FileNotFoundError:
        click.echo(f"❌ Debate '{debate_id}' not found", err=True)
        raise click.ClickException(f"Debate not found: {debate_id}")
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        raise click.ClickException(str(e))


@debates_group.command(name='export')
@click.argument('debate_id')
@click.option('--output', required=True, help='Output file path')
@click.option('--format', 'export_format', default='markdown', type=click.Choice(['markdown', 'json', 'text']), help='Export format')
def debates_export_command(debate_id, output, export_format):
    """Export a debate to a file"""
    try:
        orchestrator = DebateOrchestrator()
        debate = orchestrator.get_debate(debate_id)

        # Format based on export format
        if export_format == 'markdown':
            content = format_debate_as_markdown(debate)
        elif export_format == 'json':
            import json
            content = json.dumps(debate.model_dump(mode='json'), indent=2)
        else:  # text
            content = format_debate_for_display(debate)

        # Write to file
        os.makedirs(os.path.dirname(output) or '.', exist_ok=True)
        with open(output, 'w') as f:
            f.write(content)

        click.echo(f"✅ Debate exported to {output}")

    except FileNotFoundError:
        click.echo(f"❌ Debate '{debate_id}' not found", err=True)
        raise click.ClickException(f"Debate not found: {debate_id}")
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        raise click.ClickException(str(e))


def main():
    """Entry point for CLI"""
    cli_group()


if __name__ == '__main__':
    main()
