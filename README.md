# TdLightingdesign-ich-bin-mir-selber-fremd-geworden
creating a lighting environment that is portable and minimalistic yet able to do complex stuff: combines lighting, visuals, TouchOSC interface, managing presets, CHOP DMX

## urgent TODOs
- create POST section
    - master dimmer
    - 16-bit to 2x8-bit channels
- UI for setting up parameters:
    - Moving Heads
    - Auto Layout for dimmers
- test save function (hog CHOP)
    - create OSC feedback
- patch next show
    - reuse backlighting settings from previous show


## TODOs
- collect example photos for "fremd geworden" scenes
- presets and groups
    - fixture selector
    - grouping fixtures and controlling them simultaneously
    - presets for Color, Position, FX
- rework TouchOSC patch with grid:text and auto generating and naming faders
- scene storage selector input should be rounded
- add universe to fixture settings page and optimize dmx out CHOP
- optimize projector fading from off to on - projector needs a little time to turn on which results in a brightness jump when it turns on 
- UI for OSC Settings with static ip address
- park fixtures
- create a fixture renaming function that also updates the storage table
