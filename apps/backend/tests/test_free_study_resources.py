"""Saved roadmap resources stay free and come from this forge's search."""

from __future__ import annotations

from career_forge.ai.graphs.roadmap_forge import build_research_prompts
from career_forge.ai.tools.study_plan_planner import planner_system
from career_forge.schemas.diagnosis import DiagnosisProfile, DiagnosisResponse
from career_forge.schemas.study_plan import (
    StudyPlan,
    StudyPlanNode,
    StudyPlanTask,
    StudyResource,
)
from career_forge.services.forge_context import LearnerForgeContext
from career_forge.services.free_study_resources import (
    evaluator_system,
    restrict_plan_to_free_sources,
)


def _plan(*resources: StudyResource, why_now: str = "Base para o projeto.") -> StudyPlan:
    return StudyPlan(
        goal="backend",
        learner_context_summary="summary",
        strategy="Começar pela documentação.",
        nodes=[
            StudyPlanNode(
                node_id="python-ai",
                title="Python para IA",
                why_now=why_now,
                tasks=[
                    StudyPlanTask(
                        title="Ler a documentação",
                        outcome="Explicar o conceito.",
                        evidence_prompt="Mostrar um exemplo.",
                    ),
                ],
                resources=list(resources),
            ),
        ],
    )


def test_drops_paid_hosts_including_subdomains_and_keeps_researched_free_url() -> None:
    free = "https://fastapi.tiangolo.com/"
    plan = _plan(
        StudyResource(title="FastAPI", url=free, snippet="Docs oficiais"),
        StudyResource(title="Curso", url="https://www.udemy.com/course/x/", snippet="pago"),
        StudyResource(title="Curso BR", url="https://br.udemy.com/course/x/", snippet="pago"),
    )

    cleaned = restrict_plan_to_free_sources(
        plan,
        research_urls={free, "https://www.udemy.com/course/x/", "https://br.udemy.com/course/x/"},
    )

    assert [resource.url for resource in cleaned.nodes[0].resources] == [free]


def test_drops_linkedin_learning_and_keeps_other_linkedin_pages() -> None:
    learning = "https://www.linkedin.com/learning/python"
    post = "https://www.linkedin.com/posts/someone-activity"
    plan = _plan(
        StudyResource(title="Trilha", url=learning, snippet="curso"),
        StudyResource(title="Post", url=post, snippet="nota"),
    )

    cleaned = restrict_plan_to_free_sources(plan, research_urls={learning, post})

    assert [resource.url for resource in cleaned.nodes[0].resources] == [post]


def test_drops_url_the_search_did_not_return() -> None:
    cited = "https://fastapi.tiangolo.com/"
    invented = "https://docs.python.org/3/tutorial/"
    plan = _plan(
        StudyResource(title="FastAPI", url=cited, snippet="docs"),
        StudyResource(title="Python", url=invented, snippet="tutorial"),
    )

    cleaned = restrict_plan_to_free_sources(plan, research_urls={cited})

    assert [resource.url for resource in cleaned.nodes[0].resources] == [cited]


def test_drops_resource_whose_title_or_snippet_names_a_paid_platform() -> None:
    docs = "https://developer.mozilla.org/docs/Web/HTTP"
    video = "https://www.youtube.com/watch?v=abc"
    plan = _plan(
        StudyResource(title="Curso na Udemy", url=docs, snippet="HTTP"),
        StudyResource(title="Vídeo", url=video, snippet="Veja na Alura"),
        StudyResource(title="MDN", url=docs, snippet="Referência"),
    )

    cleaned = restrict_plan_to_free_sources(plan, research_urls={docs, video})

    assert [resource.title for resource in cleaned.nodes[0].resources] == ["MDN"]


def test_keeps_free_third_parties_that_are_not_on_the_paid_list() -> None:
    urls = [
        "https://www.youtube.com/watch?v=abc",
        "https://medium.com/some-free-post",
        "https://github.com/fastapi/fastapi",
        "https://roadmap.sh/python",
        "https://www.freecodecamp.org/news/python/",
    ]
    plan = _plan(
        *(
            StudyResource(title="Fonte", url=url, snippet="grátis")
            for url in urls
        ),
    )

    cleaned = restrict_plan_to_free_sources(plan, research_urls=set(urls))

    assert [resource.url for resource in cleaned.nodes[0].resources] == urls


def test_removes_only_the_sentence_that_names_a_paid_platform() -> None:
    plan = _plan(why_now="Leia a doc. Faça o curso da Udemy para praticar.")
    plan = plan.model_copy(
        update={"strategy": "Use a Alura. Depois leia a doc."},
    )
    plan.nodes[0].key_concepts = ["list comprehension", "Udemy"]
    plan.nodes[0].tasks[0].title = "Assista a Udemy. Depois escreva o exemplo."

    cleaned = restrict_plan_to_free_sources(plan, research_urls=set())

    assert cleaned.nodes[0].why_now == "Leia a doc."
    assert cleaned.strategy == "Depois leia a doc."
    assert cleaned.nodes[0].key_concepts == ["list comprehension"]
    assert cleaned.nodes[0].tasks[0].title == "Depois escreva o exemplo."
    assert cleaned.nodes[0].tasks


def test_keeps_a_dotted_name_when_the_sentence_only_mentions_a_platform() -> None:
    whole = _plan(why_now="Evite a Udemy no Node.js.")
    split = _plan(why_now="Leia Node.js. Faça o curso da Udemy para praticar.")

    assert restrict_plan_to_free_sources(whole, set()).nodes[0].why_now == (
        "Evite a no Node.js."
    )
    assert restrict_plan_to_free_sources(split, set()).nodes[0].why_now == "Leia Node.js."


def test_drops_every_sentence_that_names_a_platform_and_keeps_the_field() -> None:
    plan = _plan(why_now="Curso da Udemy. Assinatura da Alura.")

    cleaned = restrict_plan_to_free_sources(plan, set(), locale="pt-BR")

    assert cleaned.nodes[0].why_now == "Segue a trilha."


def test_strips_the_platform_name_when_it_is_the_whole_field() -> None:
    plan = _plan(why_now="Faça o curso da Udemy.")
    plan.nodes[0].tasks[0].outcome = "Publicar o exercício da Coursera."

    cleaned = restrict_plan_to_free_sources(plan, research_urls=set())

    assert cleaned.nodes[0].why_now == "Faça o curso da."
    assert cleaned.nodes[0].tasks[0].outcome == "Publicar o exercício da."
    assert cleaned.nodes[0].tasks[0].title == "Ler a documentação"


def test_keeps_a_required_field_when_the_text_is_only_the_platform_name() -> None:
    plan = _plan(why_now="Udemy.")

    cleaned = restrict_plan_to_free_sources(plan, set(), locale="pt-BR")

    assert cleaned.nodes[0].why_now == "Segue a trilha."


def test_keeps_a_required_field_when_the_text_is_only_the_platform_name_without_punctuation() -> None:
    plan = _plan(why_now="Udemy")
    plan.nodes[0].tasks[0].evidence_prompt = "Alura"

    cleaned = restrict_plan_to_free_sources(plan, set(), locale="pt-BR")

    assert cleaned.nodes[0].why_now == "Segue a trilha."
    assert "udemy" not in cleaned.nodes[0].why_now.lower()
    assert cleaned.nodes[0].tasks[0].evidence_prompt == "Mostrar o que fez."
    assert cleaned.nodes[0].tasks


def test_allows_a_node_with_no_resources() -> None:
    plan = _plan()

    cleaned = restrict_plan_to_free_sources(plan, research_urls=set())

    assert cleaned.nodes[0].resources == []


def test_prompts_ask_for_free_sources_and_name_the_closed_list() -> None:
    context = LearnerForgeContext(
        user_id="learner",
        goal_id="backend",
        motivation="APIs",
        diagnosis=DiagnosisResponse(
            profile=DiagnosisProfile(label="Iniciante", track_id="backend-beginner"),
            strengths=["prática"],
            gaps=["APIs"],
            starting_priorities=["HTTP"],
        ),
    )
    prompts = build_research_prompts(context)
    system = planner_system("en")
    evaluation = evaluator_system(["https://fastapi.tiangolo.com/"])

    assert len(prompts) == 3
    assert all("without paying" in prompt for prompt in prompts)
    assert all("Portuguese" in prompt for prompt in prompts)
    assert all("Udemy" in prompt for prompt in prompts)
    assert "research_state" in system
    assert "leave resources empty" in system
    assert "https://fastapi.tiangolo.com/" in evaluation
    assert "mark revise" in evaluation.lower()
