# Skyscraper Stack Repair Lab

Skyscraper Stack is a Pygame precision-timing tower game. The player moves blocks horizontally and drops them onto the tower. Successful drops trim overhangs, while increasingly tall towers trigger camera scrolling and atmospheric background changes.

Tasks 1-4 are implemented in the current source.

## Project structure

```text
.
|-- main.py
|-- README.md
`-- game/
    |-- block.py
    `-- game_engine.py
```

- `main.py` initializes Pygame and runs the 60 FPS application loop.
- `game/block.py` defines `Block` and the independent falling `Debris` object.
- `game/game_engine.py` owns game state, input, placement, scoring, camera shifting, background rendering, and the Game Over screen.

Generated `game/__pycache__/` files are runtime artifacts and are not part of the source structure.

## Setup and run

Requirements:

- Python 3.10 or newer
- Pygame

Install Pygame:

```bash
pip install pygame
```

Run the game from the project directory:

```bash
python main.py
```

## Controls

- During play, press `Space` or left-click to drop the active block.
- After Game Over, press `R` or left-click to restart.
- `Space` does not restart after Game Over.
- Close the game window to quit.

## Game rules and state

- The foundation block starts at the bottom of the arena.
- The active block moves horizontally and bounces between the screen margins.
- Movement speed increases with the number of stack blocks, up to a maximum speed.
- A placement succeeds only when the horizontal overlap is positive.
- Zero or negative overlap causes Game Over.
- A normal successful placement trims the active block to the intersection with the previous top block.
- The minimum block width is 10 pixels.

The HUD displays two separate values:

- `Height`: placed blocks above the foundation, calculated as `len(stack) - 1`.
- `Score`: normal placement points plus perfect-placement bonuses.

## Implemented tasks

### Task 1: Correct overlap placement logic

`drop_block()` treats `overlap > 0` as a successful placement. A zero or negative overlap triggers Game Over.

### Task 2: Perfect placement and width restoration

- Alignment within 3 pixels of the previous top block is perfect.
- A normal placement awards 1 point.
- A perfect placement awards 3 points total: 1 placement point plus a 2-point bonus.
- Perfect placements preserve the active block width instead of trimming it.
- A golden `PERFECT!` popup lasts for 60 update frames, approximately one second at 60 FPS.
- Consecutive perfect placements form a streak.
- Every third consecutive perfect placement restores 10 pixels of width.
- Width is clamped between 10 pixels and the original 180-pixel base width.
- A successful non-perfect placement resets the perfect streak.

### Task 3: Falling off-cut debris

When a normal placement trims a positive left or right overhang, the removed rectangle becomes an independent debris object. Debris:

- Falls under gravity.
- Moves away from the tower.
- Rotates while falling.
- Is rendered separately from the stack.
- Is removed after leaving the screen.

Debris does not affect collision, score, height, placement, or camera decisions. Perfect placements do not create debris because they do not trim an overhang.

### Task 4: Height-based atmospheric background

The background uses the number of placed blocks above the foundation, not the score. It is drawn as a smooth vertical gradient and transitions through these height ranges:

| Tower height | Stage |
|---:|---|
| 0-4 | Twilight blue |
| 5-9 | Dusk purple |
| 10-19 | Deep night blue |
| 20 and above | Stratosphere black |

The final stratosphere stage is clamped for very tall towers. Stars are generated once during reset with a local seeded generator, so their positions remain stable between frames. They fade in during the dusk-to-night transition and are strongest in the night stages.

## Camera scrolling

When the newly placed block reaches above the vertical threshold (`y < 180`), the stack is shifted downward by 32 pixels. Existing debris is shifted with the stack so it remains visually consistent. This is a discrete camera offset adjustment, not a continuously animated camera pan.

## Game Over and restart

After a missed placement, the game displays a dark Game Over overlay with:

- Final tower height
- Final score
- Restart instructions

The active block stops moving, but existing debris continues its visual animation. Pressing `R` or left-click calls `reset()`, which restores the base tower, score, perfect streak, popup state, debris, and initial twilight background.

## Testing and validation

There is no checked-in automated test suite. The implementation has been validated with:

- Python syntax checks for all source files.
- Deterministic logic checks for positive, zero, and negative overlap.
- Perfect-placement score, popup, streak, width, and reset checks.
- Debris geometry, motion, cleanup, and isolation checks.
- Background interpolation, star stability, night visibility, clamping, restart, and foreground-render checks.

For final manual validation after installing Pygame, record a run showing:

1. A successful normal overlap and trimmed block.
2. A perfect placement with the popup and bonus score.
3. A third consecutive perfect placement restoring width.
4. A trimmed placement producing falling debris.
5. The background changing as the tower grows.
6. A missed placement causing Game Over.
7. Restart using `R` and left-click.

## Submission checklist

- [ ] 10-second video before the changes showing the original overlap bug, if required by the lab.
- [ ] 10-second video after the changes showing the corrected behavior and implemented features.
- [ ] Link to the Chat/LLM page containing the complete conversation history.
