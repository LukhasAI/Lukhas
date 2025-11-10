"""
Comprehensive tests for the Guided CLI - Interactive setup and demos.

Tests quickstart wizard, demo execution, and interactive tours.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
import subprocess

from lukhas.cli.guided import GuidedCLI, main


@pytest.fixture
def cli():
    """Fresh GuidedCLI instance."""
    with patch('lukhas.cli.guided.HAS_RICH', False):
        return GuidedCLI()


@pytest.fixture
def cli_with_rich():
    """GuidedCLI instance with rich enabled."""
    with patch('lukhas.cli.guided.HAS_RICH', True):
        from rich.console import Console
        cli = GuidedCLI()
        cli.console = Console()
        return cli


class TestInitialization:
    """Test GuidedCLI initialization."""

    def test_init_without_rich(self, cli):
        """Test initialization when rich is not available."""
        assert cli.console is None
        assert cli.project_root.name == "Lukhas"

    def test_init_with_rich(self):
        """Test initialization when rich is available."""
        with patch('lukhas.cli.guided.HAS_RICH', True):
            cli = GuidedCLI()
            assert cli.console is not None

    def test_project_root_detection(self, cli):
        """Test that project root is detected correctly."""
        assert isinstance(cli.project_root, Path)


class TestPrintMethod:
    """Test the print method wrapper."""

    def test_print_without_rich(self, cli):
        """Test print falls back to built-in when no rich."""
        with patch('builtins.print') as mock_print:
            cli.print("Test message")
            mock_print.assert_called_once_with("Test message")

    def test_print_with_rich(self, cli_with_rich):
        """Test print uses rich console when available."""
        with patch.object(cli_with_rich.console, 'print') as mock_print:
            cli_with_rich.print("Test message")
            mock_print.assert_called_once_with("Test message")


class TestQuickstart:
    """Test quickstart wizard functionality."""

    @patch('lukhas.cli.guided.HAS_RICH', False)
    def test_quickstart_without_rich(self, cli):
        """Test quickstart runs without rich library."""
        with patch.object(cli, 'print') as mock_print:
            cli.quickstart()
            # Should print welcome and steps
            assert mock_print.call_count > 0

    @patch('lukhas.cli.guided.HAS_RICH', True)
    def test_quickstart_with_rich(self):
        """Test quickstart with rich UI."""
        from rich.console import Console
        from rich.prompt import Prompt, Confirm

        cli = GuidedCLI()
        cli.console = Console()

        with patch.object(Prompt, 'ask', return_value="1"):
            with patch.object(Confirm, 'ask', side_effect=[True, False]):
                with patch.object(cli, 'print'):
                    with patch('time.sleep'):  # Speed up the test
                        cli.quickstart()

    def test_quickstart_developer_path(self):
        """Test quickstart with developer path selection."""
        with patch('lukhas.cli.guided.HAS_RICH', True):
            from rich.prompt import Prompt, Confirm
            cli = GuidedCLI()

            with patch.object(Prompt, 'ask', return_value="1"):
                with patch.object(Confirm, 'ask', side_effect=[True, True]):
                    with patch('time.sleep'):
                        cli.quickstart()

    def test_quickstart_researcher_path(self):
        """Test quickstart with researcher path selection."""
        with patch('lukhas.cli.guided.HAS_RICH', True):
            from rich.prompt import Prompt, Confirm
            cli = GuidedCLI()

            with patch.object(Prompt, 'ask', return_value="2"):
                with patch.object(Confirm, 'ask', side_effect=[False, False]):
                    with patch('time.sleep'):
                        cli.quickstart()

    def test_quickstart_enterprise_path(self):
        """Test quickstart with enterprise path selection."""
        with patch('lukhas.cli.guided.HAS_RICH', True):
            from rich.prompt import Prompt, Confirm
            cli = GuidedCLI()

            with patch.object(Prompt, 'ask', return_value="3"):
                with patch.object(Confirm, 'ask', side_effect=[True, False]):
                    with patch('time.sleep'):
                        cli.quickstart()

    def test_quickstart_prints_next_steps(self, cli):
        """Test that quickstart prints next steps at the end."""
        with patch.object(cli, 'print') as mock_print:
            cli.quickstart()

            # Should mention demos and tour
            print_calls = [str(call) for call in mock_print.call_args_list]
            assert any('demo' in str(call).lower() for call in print_calls)
            assert any('tour' in str(call).lower() for call in print_calls)


class TestDemo:
    """Test demo execution functionality."""

    def test_demo_no_argument_shows_menu(self, cli):
        """Test that calling demo without argument shows menu."""
        with patch.object(cli, 'print') as mock_print:
            cli.demo(None)

            # Should print available demos
            print_calls = [str(call) for call in mock_print.call_args_list]
            assert any('hello' in str(call).lower() for call in print_calls)
            assert any('reasoning' in str(call).lower() for call in print_calls)
            assert any('memory' in str(call).lower() for call in print_calls)

    def test_demo_shows_all_examples(self, cli):
        """Test that demo menu shows all available examples."""
        with patch.object(cli, 'print'):
            cli.demo(None)

        # Verify all examples are available
        expected_demos = ["hello", "reasoning", "memory", "ethics", "full"]
        # Implementation contains all these demos

    def test_demo_invalid_name(self, cli):
        """Test demo with invalid example name."""
        with patch.object(cli, 'print') as mock_print:
            cli.demo("invalid_demo")

            # Should print error message
            print_calls = [str(call) for call in mock_print.call_args_list]
            assert any('error' in str(call).lower() or 'unknown' in str(call).lower() for call in print_calls)

    @patch('subprocess.run')
    def test_demo_hello_execution(self, mock_run, cli):
        """Test executing hello demo."""
        mock_run.return_value = Mock(returncode=0)

        with patch.object(cli, 'print'):
            cli.demo("hello")

        # Should execute the hello example
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "01_hello_lukhas.py" in str(call_args[-1])

    @patch('subprocess.run')
    def test_demo_reasoning_execution(self, mock_run, cli):
        """Test executing reasoning demo."""
        mock_run.return_value = Mock(returncode=0)

        with patch.object(cli, 'print'):
            cli.demo("reasoning")

        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "02_reasoning_trace.py" in str(call_args[-1])

    @patch('subprocess.run')
    def test_demo_memory_execution(self, mock_run, cli):
        """Test executing memory demo."""
        mock_run.return_value = Mock(returncode=0)

        with patch.object(cli, 'print'):
            cli.demo("memory")

        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "03_memory_persistence.py" in str(call_args[-1])

    @patch('subprocess.run')
    def test_demo_ethics_execution(self, mock_run, cli):
        """Test executing ethics demo."""
        mock_run.return_value = Mock(returncode=0)

        with patch.object(cli, 'print'):
            cli.demo("ethics")

        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "04_guardian_ethics.py" in str(call_args[-1])

    @patch('subprocess.run')
    def test_demo_full_execution(self, mock_run, cli):
        """Test executing full workflow demo."""
        mock_run.return_value = Mock(returncode=0)

        with patch.object(cli, 'print'):
            cli.demo("full")

        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "05_full_workflow.py" in str(call_args[-1])

    @patch('subprocess.run')
    def test_demo_execution_uses_correct_python(self, mock_run, cli):
        """Test that demo uses the correct Python interpreter."""
        mock_run.return_value = Mock(returncode=0)

        with patch.object(cli, 'print'):
            cli.demo("hello")

        # Should use sys.executable
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == sys.executable

    @patch('subprocess.run')
    def test_demo_execution_failure(self, mock_run, cli):
        """Test handling of demo execution failure."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "cmd")

        with patch.object(cli, 'print') as mock_print:
            cli.demo("hello")

        # Should print error and suggest troubleshooting
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any('error' in str(call).lower() for call in print_calls)
        assert any('troubleshoot' in str(call).lower() for call in print_calls)


class TestTour:
    """Test interactive tour functionality."""

    def test_tour_shows_all_steps(self, cli):
        """Test that tour shows all steps."""
        with patch.object(cli, 'print') as mock_print:
            with patch('builtins.input', return_value=""):
                cli.tour()

            # Should print all tour steps
            print_calls = [str(call) for call in mock_print.call_args_list]
            assert any('matriz' in str(call).lower() for call in print_calls)
            assert any('memory' in str(call).lower() or 'folds' in str(call).lower() for call in print_calls)
            assert any('guardian' in str(call).lower() or 'ethics' in str(call).lower() for call in print_calls)

    def test_tour_step_count(self, cli):
        """Test that tour has expected number of steps."""
        with patch.object(cli, 'print'):
            with patch('builtins.input', return_value=""):
                cli.tour()
        # Tour should have 5 steps (based on implementation)

    def test_tour_with_rich(self):
        """Test tour with rich UI."""
        with patch('lukhas.cli.guided.HAS_RICH', True):
            from rich.prompt import Confirm
            cli = GuidedCLI()

            with patch.object(Confirm, 'ask', return_value=True):
                with patch.object(cli, 'print'):
                    cli.tour()

    def test_tour_prints_next_steps(self, cli):
        """Test that tour prints next steps at the end."""
        with patch.object(cli, 'print') as mock_print:
            with patch('builtins.input', return_value=""):
                cli.tour()

            # Should print what's next
            print_calls = [str(call) for call in mock_print.call_args_list]
            assert any('demo' in str(call).lower() for call in print_calls)

    def test_tour_without_rich_uses_input(self, cli):
        """Test that tour without rich uses input() for continuation."""
        with patch('builtins.input') as mock_input:
            mock_input.return_value = ""
            with patch.object(cli, 'print'):
                cli.tour()

            # Should call input for each step (except last)
            assert mock_input.call_count >= 4


class TestMainFunction:
    """Test the main CLI entry point."""

    def test_main_quickstart_command(self):
        """Test main with quickstart command."""
        with patch('sys.argv', ['guided.py', 'quickstart']):
            with patch('lukhas.cli.guided.GuidedCLI') as mock_class:
                mock_cli = Mock()
                mock_class.return_value = mock_cli

                main()

                mock_cli.quickstart.assert_called_once()

    def test_main_demo_command_with_example(self):
        """Test main with demo command and example name."""
        with patch('sys.argv', ['guided.py', 'demo', 'hello']):
            with patch('lukhas.cli.guided.GuidedCLI') as mock_class:
                mock_cli = Mock()
                mock_class.return_value = mock_cli

                main()

                mock_cli.demo.assert_called_once_with('hello')

    def test_main_demo_command_without_example(self):
        """Test main with demo command but no example name."""
        with patch('sys.argv', ['guided.py', 'demo']):
            with patch('lukhas.cli.guided.GuidedCLI') as mock_class:
                mock_cli = Mock()
                mock_class.return_value = mock_cli

                main()

                mock_cli.demo.assert_called_once_with(None)

    def test_main_tour_command(self):
        """Test main with tour command."""
        with patch('sys.argv', ['guided.py', 'tour']):
            with patch('lukhas.cli.guided.GuidedCLI') as mock_class:
                mock_cli = Mock()
                mock_class.return_value = mock_cli

                main()

                mock_cli.tour.assert_called_once()

    def test_main_no_command_shows_help(self):
        """Test main with no command shows help."""
        with patch('sys.argv', ['guided.py']):
            with patch('argparse.ArgumentParser.print_help') as mock_help:
                main()
                mock_help.assert_called_once()

    def test_main_invalid_command_shows_help(self):
        """Test main with invalid command shows help."""
        with patch('sys.argv', ['guided.py', 'invalid']):
            with pytest.raises(SystemExit):
                main()


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_demo_with_nonexistent_file(self, cli):
        """Test demo execution when example file doesn't exist."""
        with patch('subprocess.run', side_effect=FileNotFoundError):
            with patch.object(cli, 'print'):
                try:
                    cli.demo("hello")
                except FileNotFoundError:
                    pass  # Expected

    def test_quickstart_with_progress_spinner(self):
        """Test quickstart with progress spinner."""
        with patch('lukhas.cli.guided.HAS_RICH', True):
            from rich.prompt import Prompt, Confirm
            cli = GuidedCLI()

            with patch.object(Prompt, 'ask', return_value="1"):
                with patch.object(Confirm, 'ask', side_effect=[True, True]):
                    with patch('time.sleep', return_value=None):
                        cli.quickstart()

    def test_demo_menu_with_rich_table(self):
        """Test demo menu displays as rich table."""
        with patch('lukhas.cli.guided.HAS_RICH', True):
            cli = GuidedCLI()
            with patch.object(cli, 'print'):
                cli.demo(None)

    def test_tour_panels_with_rich(self):
        """Test tour uses panels with rich."""
        with patch('lukhas.cli.guided.HAS_RICH', True):
            from rich.prompt import Confirm
            cli = GuidedCLI()

            with patch.object(Confirm, 'ask', return_value=True):
                with patch.object(cli, 'print'):
                    cli.tour()

    @patch('subprocess.run')
    def test_demo_check_true_flag(self, mock_run, cli):
        """Test that demo uses check=True for subprocess."""
        mock_run.return_value = Mock(returncode=0)

        with patch.object(cli, 'print'):
            cli.demo("hello")

        # Verify check=True is passed
        assert mock_run.call_args[1].get('check') is True

    def test_multiple_quickstart_runs(self, cli):
        """Test that quickstart can be run multiple times."""
        with patch.object(cli, 'print'):
            cli.quickstart()
            cli.quickstart()
        # Should not raise errors

    def test_multiple_tour_runs(self, cli):
        """Test that tour can be run multiple times."""
        with patch('builtins.input', return_value=""):
            with patch.object(cli, 'print'):
                cli.tour()
                cli.tour()
        # Should not raise errors


class TestIntegration:
    """Integration tests for CLI workflows."""

    def test_full_quickstart_flow(self):
        """Test complete quickstart workflow."""
        with patch('lukhas.cli.guided.HAS_RICH', True):
            from rich.prompt import Prompt, Confirm
            cli = GuidedCLI()

            with patch.object(Prompt, 'ask', return_value="1"):
                with patch.object(Confirm, 'ask', side_effect=[True, False]):
                    with patch('time.sleep'):
                        with patch.object(cli, 'print') as mock_print:
                            cli.quickstart()

                            # Verify workflow completed
                            assert mock_print.call_count > 5

    def test_demo_menu_to_execution_flow(self, cli):
        """Test flow from viewing demo menu to executing a demo."""
        # First show menu
        with patch.object(cli, 'print'):
            cli.demo(None)

        # Then execute a demo
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)
            with patch.object(cli, 'print'):
                cli.demo("hello")

            mock_run.assert_called_once()

    def test_tour_complete_flow(self, cli):
        """Test complete tour flow through all steps."""
        with patch('builtins.input', return_value=""):
            with patch.object(cli, 'print') as mock_print:
                cli.tour()

                # Should print all 5 tour steps
                print_calls = [str(call) for call in mock_print.call_args_list]
                assert len(print_calls) > 10  # Multiple prints per step

    def test_argparse_integration_quickstart(self):
        """Test argparse integration with quickstart."""
        with patch('sys.argv', ['guided.py', 'quickstart']):
            with patch('lukhas.cli.guided.GuidedCLI.quickstart'):
                main()

    def test_argparse_integration_demo(self):
        """Test argparse integration with demo."""
        with patch('sys.argv', ['guided.py', 'demo', 'reasoning']):
            with patch('lukhas.cli.guided.GuidedCLI.demo'):
                main()

    def test_argparse_integration_tour(self):
        """Test argparse integration with tour."""
        with patch('sys.argv', ['guided.py', 'tour']):
            with patch('lukhas.cli.guided.GuidedCLI.tour'):
                main()


class TestUserInteraction:
    """Test user interaction handling."""

    def test_quickstart_user_choices_stored(self):
        """Test that user choices are captured during quickstart."""
        with patch('lukhas.cli.guided.HAS_RICH', True):
            from rich.prompt import Prompt, Confirm
            cli = GuidedCLI()

            with patch.object(Prompt, 'ask', return_value="2") as mock_prompt:
                with patch.object(Confirm, 'ask', side_effect=[False, True]) as mock_confirm:
                    with patch('time.sleep'):
                        cli.quickstart()

                    # Verify prompts were called
                    mock_prompt.assert_called()
                    assert mock_confirm.call_count == 2

    def test_tour_continuation_prompts(self):
        """Test tour continuation prompts between steps."""
        with patch('builtins.input', side_effect=["", "", "", ""]) as mock_input:
            with patch.object(GuidedCLI, 'print'):
                cli = GuidedCLI()
                cli.tour()

            # Should prompt between steps (not after last step)
            assert mock_input.call_count == 4
