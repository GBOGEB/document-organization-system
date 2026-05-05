# Idempotent and Recursive Control Logic

## Idempotent principle

The tool must be repeatable:

```text
Same version + same inputs + same method + same coefficients = same outputs.
```

This is important because engineering calculations must be traceable and reviewable.

## Idempotent requirements

1. Do not silently change coefficients.
2. Do not silently change equation form.
3. Do not silently change integration method.
4. Do not silently change default units.
5. Do not silently change default T1/T2 or geometry values.
6. Every version change must have a changelog entry.
7. Any coefficient correction must identify the affected material/property.
8. Any validation change must identify whether it affects values or only display.

## Recursive development loop

The development process used in the session:

```text
Build -> Review -> Detect issue -> Diagnose -> Fix -> Version -> Re-test -> Document -> Repeat
```

Applied examples:

```text
Static preview looked inactive
-> added output cards and buttons
-> buttons were non-responsive
-> removed fragile dependencies
-> material dropdown still failed
-> hardcoded material options
-> added self-test/fallback
-> equation visibility added
-> user review found clarity/integration issues
-> debug v1.10 built
```

## DMAIC-recursive mapping

```text
Define    -> Reconfirm problem and user context.
Measure   -> Capture inputs, outputs, failures, and expected checks.
Analyze   -> Identify exact mismatch or unclear behavior.
Improve   -> Apply minimal controlled fix.
Control   -> Version, changelog, validation checklist, and handover notes.
```

## Rule for future coding agents

Never jump directly to new features if validation findings exist.

Priority order:

```text
1. Correctness
2. Traceability
3. Repeatability
4. Usability
5. Visual polish
6. New features
```

