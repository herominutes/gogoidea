# Designing the 7-day tests

The council's output is a hypothesis worth testing, not a green light to build. A good test attacks the **riskiest assumption**, is **pre-registered** before it runs, and ends in a decision nobody can reinterpret afterward.

Contents: [Principles](#principles) · [Commitment ladder](#commitment-ladder) · [Test menu](#test-menu) · [Pre-registration template](#pre-registration-template) · [Reading small samples](#reading-small-samples) · [Outreach ethics](#outreach-ethics) · [After the test](#after-the-test)

## Principles

- **Test the assumption most likely to kill it.** Take the top entry from `assumptions.md` (impact if wrong × uncertainty). If the riskiest assumption is "buyers will pay", don't test whether they like the logo.
- **Pre-register.** Write the pass bar and kill criteria before anyone sends a message or ships a page. Decisions made after seeing results tend to rescue the idea.
- **Behaviour beats opinion.** Praise costs nothing. Climb the ladder below; the higher the rung, the more it counts.
- **Don't iterate the pitch mid-test.** Changing the message restarts the test. Tuning until something works measures your persistence, not demand.
- **Smallest honest test.** Fake, manual and concierge versions are fine as long as no one is deceived about what they're buying.

## Commitment ladder

From weakest to strongest signal. Record the highest rung each person reached.

1. Positive reply ("interesting")
2. Answers a specific question about their current workflow
3. Takes a call / screen-share
4. Joins a waitlist with a real email
5. Agrees to a pilot with a date
6. **Pays** (refundable deposit, pre-order or first month)

A test with many rung-1 replies and no rung-4+ is a failure that looks like a success.

## Test menu

| Test | Attacks | Shape | When |
|---|---|---|---|
| **Desirability outreach** | "Do they care enough to engage?" | 100 messages to identified buyers in the communities the evidence came from; ask a real question and make an honest offer | Default for every winner |
| **Price / fake-door** | "Will they pay this price?" | One landing page, one price, one button (pre-order or refundable deposit); drive traffic from the same communities | When money is the riskiest assumption |
| **Concierge / manual MVP** | "Does the outcome matter, and is the workflow right?" | Deliver the result by hand for 3–5 customers | When the service blueprint shows heavy hidden complexity |
| **Feasibility spike** | "Can I build the hard part?" | One day on the riskiest technical piece (e-sign, import, integration) | When the builder said `SHIPPABLE IF` |
| **Switching-cost probe** | "Will they move their data/history?" | Ask 10 users of the incumbent what it would take; offer to migrate one by hand | When switch anxiety is the skeptic's top concern |

Standard mode designs two tests (desirability + the one that hits the riskiest assumption); exhaustive designs three (desirability, price, feasibility).

## Pre-registration template

```markdown
## Test: <name>
- **Assumption tested:** <from assumptions.md>
- **Audience & where to find them:** <specific communities, lists, search phrases from the evidence>
- **Action:** <what exactly is sent/built; include the message or page copy>
- **Volume & window:** <e.g. 100 messages over 7 days>
- **Pass bar:** <e.g. ≥5 replies reaching rung 3+ AND ≥1 pre-payment>
- **Kill criteria:** <e.g. <5% replies OR zero rung-4+ → drop the idea>
- **Decision if pass:** <build the v1 and nothing more>
- **Decision if fail:** <park the idea; rerun the council with what was learned added to the brief>
- **Decided before running:** <date/time>
```

## Reading small samples

Tiny samples are wide. A 5% reply rate from 100 messages has a 95% interval of roughly **2%–11%**; 0 of 30 doesn't rule out 10%. Treat the test as a **screen** that rejects clearly dead ideas and promotes plausible ones — not as proof. That's why the bar mixes a reply rate with a **hard behavioural event** (a payment, a dated pilot): one real payment says more than a pile of "nice idea".

## Outreach ethics

- Be honest about what exists. "I'm building X — would this help? early access if so" is fine; implying a finished product is not.
- One message per person. No bulk blasts, no scraping private contact data, no impersonation.
- Follow each community's self-promotion rules; read them first, and ask moderators when unclear.
- Make opting out easy and stop immediately when asked.
- Take money only if you can deliver or refund; use a refundable deposit when the product doesn't exist yet, and follow the payment provider's rules for pre-orders.

## After the test

- **Pass:** build exactly the v1 in the pitch. Resist adding what the skeptic or taste editor said to cut.
- **Fail:** record why in the ledger, park the idea, and rerun the council with what you learned (new language, a narrower segment, the real objection) added to the brief. The runner-up is the next candidate.
- **Ambiguous:** extend with *new* people, not more messages to the same ones.
