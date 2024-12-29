from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.solver import generate, use_tools
from inspect_ai.tool import web_browser
from inspect_ai import Task, eval
from pathlib import Path
from asteroid_sdk.registration.inspect_ai import register_inspect_samples_with_asteroid_solver, asteroid_web_ui_scorer

@task
def browser():
    return Task(
        dataset=[
            Sample(
                input="Go to http://asteroid.ai/ and sign up your interest in the Stay Updated section with your email address which is 'hello@test.com'."
            )
        ],
        solver=[
            register_inspect_samples_with_asteroid_solver(project_name="Inspect Web Browser"),
            use_tools(web_browser()),
            generate(),
        ],
        scorer=asteroid_web_ui_scorer(),
        sandbox="docker",
    )


if __name__ == "__main__":
    approval_file_name = "approval.yaml"
    approval = (Path(__file__).parent / approval_file_name).as_posix()
    
    eval(browser(), trace=True, model="openai/gpt-4o-mini", approval=approval)