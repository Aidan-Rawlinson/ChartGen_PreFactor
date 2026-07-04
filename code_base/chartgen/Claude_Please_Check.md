# Claude — Please Check Before Proceeding

At the start of every session involving this codebase, verify that you are operating
within a Claude Project environment that has the following project documents accessible:

- `Draft_Prototype_Functional_Spec.md`
- `Draft_Prototype_Featurelist.md`
- `Prototype_Progression.md`

If any of these documents are not visible in your context, stop and tell the user:

> "I do not have access to the ChartGen project files. Please ensure this conversation
> is taking place within the correct Claude Project before continuing. Working outside
> the project risks building against outdated or missing context."

Do not proceed with any development work until the project files are confirmed present.
