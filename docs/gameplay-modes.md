# Classic and Extended

A new game asks for Classic or Erweitert before gender selection and Oak's
introduction. In-game, hold Select for about three seconds in Start → OPTION,
release it, move Down to SPIELMODUS, choose with Left/Right and confirm with A.
B/Start or ZURÜCK cancel. The choice is stored by ordinary in-game saving.
Existing saves require no restart; old unselected saves default to Classic.

Implemented mode differences:

- Classic: normal walking speed; the HUD and empty EXP track remain in battle/status; only blue EXP fill is hidden.
- Extended: existing EXP bar and its gain animation; hold B while walking to
  move at twice normal walking speed, including inside buildings.
- EXP itself, levels, battle rules, sprites, item capacities and all other
  currently implemented features are otherwise unchanged.
- B adds no speed while surfing, cycling, jumping, spinning or scripted walking.
  Cycling keeps its original behavior. Releasing or pressing B partway through
  a step cannot underflow the movement counter. No dedicated running art or
  additional running-shoe unlock event is introduced.

The mode is persisted in feature schema 1, with a derived normal-WRAM mirror.
Switching modes resets EXP-bar animation bookkeeping. Menus cannot switch modes
mid-battle, so the battle/status HUD reflects the current choice on next draw.
Future map/event features may apply their mode at natural reload points.

Regression tests cover both initial choices, hidden-menu changes, persistence,
Classic empty track / Extended filled bar, guarded movement advancement,
mid-step counter safety and actual overworld walking distances with B held.
The existing tests also cover migration, storage and font/menu integrity. This
is not a full campaign or exhaustive battle-animation playthrough.

New-game gender selection uses the same standard box and vertical choice layout
as the mode selection. Girl name suggestions are Grün, Elly and Tina. The
hidden-menu gender symbols occupy evenly spaced columns 5 and 14.
