# GhostNet design notes

Owner: UI and UX Designer (member 9)

## The one rule

The interface must never show a name next to a score. Anonymity is the product,
so if a screen leaks identity the screen is wrong, not the policy.

That rule is enforced twice. The API never selects the real name column while
ranking, and the TypeScript type carries the name as nullable so the compiler
complains if a component tries to print it early.

## Screen flow

```
Challenges  ->  One challenge  ->  Ranking table  ->  Reveal
                     |
                     +-- Submit anonymously
```

Four steps, and the demo is meant to be walked in that order. Matching,
Schedule and Proof chain sit beside the flow as separate pages because each one
belongs to a different member and each is shown on its own.

## Visual system

The style is brutalist and monochrome, reused from an existing project.

* Structure comes from 2px black borders and hard offset shadows, not from soft
  shadows, so nothing depends on colour to read as a boundary
* Colour appears only where it carries data, such as a red plagiarism badge or
  a green kept window on the timeline
* Every number uses a monospace face so the score columns line up
* One inverted card in the whole app, the winner card, because that is the one
  moment where anonymity ends and it should feel different

All of it comes from the tokens at the top of `globals.css`. Changing the theme
means editing that one block, not hunting through components.

## Why each screen looks the way it does

**Ranking table.** Every column header carries the algorithm that produced the
number underneath it, so the table doubles as the viva slide. Headers are
clickable, and the reorder runs merge sort in the browser rather than asking the
server again.

**Schedule.** Intervals are drawn as bars on a shared timeline instead of listed
as numbers. A greedy choice is easy to argue about when the overlap is visible
and hard to argue about when it is two columns of integers.

**Proof chain.** Each block prints the previous hash directly above its own
hash, so the link is something you read rather than something we assert.

## Accessibility

Contrast is carried by the black borders rather than by fill colour, so the
plagiarism badge still reads without colour vision. The active nav item uses
`aria-current` instead of colour alone. Every input has a real label element.
