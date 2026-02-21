# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Frontier Forge** is a 2D management/survival game built with Python and Pygame. It features both solo and multiplayer modes, combining resource gathering, base building, crafting, and defense against enemy waves.

- **Current Version**: 0.4.0
- **Technology Stack**: Python 3.8+, Pygame 2.5.0+, TCP Socket (multiplayer)
- **Game Modes**: Solo (`main.py`), Multiplayer (`main_multiplayer.py`)

## Running the Game

### Solo Mode
```bash
python main.py
```

### Multiplayer Mode
**Server (host):**
```bash
python start_server.py
# Press Enter for default port 5555
```

**Client (all players including host):**
```bash
python main_multiplayer.py
# Enter server IP (localhost for host, Hamachi IP for remote players)
# Enter port: 5555
```

### Development Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Syntax check a file
python3 -m py_compile <filename.py>

# Run from specific directory (must be in ForgeFrontier/)
cd "/mnt/c/Users/ouzdi/Desktop/Frontier Forge/ForgeFrontier"
python main.py
```

## Architecture Overview

### Core Game Loop (main.py / main_multiplayer.py)
The `Game` class orchestrates all systems:
1. **Initialization**: Sets up Pygame, creates World, Player, UI, Quest Manager, Crafting System
2. **Update Loop**: Processes input → updates entities → checks collisions → handles game state
3. **Render Loop**: Draws world → buildings → enemies → player → UI
4. **Delta Time**: All movement/timers use `delta_time` for frame-rate independence

### Component Architecture

**Core Components** (each in separate file):
- `player.py`: Player movement, inventory, stats (health, hunger)
- `world.py`: Procedural terrain generation (grass, metal, food, water, mountains, forests, deserts)
- `buildings.py`: 10 building types with production/defense/special functions
- `enemies.py`: 3 enemy types (Zombie, Mutant, Wolf) with AI targeting
- `ui.py`: HUD, resource display, building menu, quest notifications
- `constants.py`: All game configuration (costs, stats, colors, terrain types)

**Systems**:
- `crafting.py`: Manual crafting recipes + auto-crafting queue
- `quests.py`: Dynamic quest system with progression tracking
- `save_system.py`: JSON-based save/load (solo only)
- `animations.py`: Sprite animations (currently basic)
- `sprite_loader.py`: Asset loading utilities

**Network (multiplayer only)**:
- `network/protocol.py`: JSON message encoding/decoding (9 message types)
- `network/server.py`: TCP server with game state authority
- `network/client.py`: TCP client with callback system

### Building System Architecture

**10 Buildings** mapped to keys 1-9, 0:
1. Mine (1) - Metal production
2. Farm (2) - Food production
3. Generator (3) - Energy production
4. Turret (4) - Auto-defense
5. Rocket (5) - Victory objective
6. Hospital (6) - Auto-healing
7. Laboratory (7) - Research upgrades (5 levels)
8. Wall (8) - Passive defense with durability
9. Warehouse (9) - Multi-resource production
10. Factory (0) - Auto-crafting assigned recipe

**Building Interface**: `buildings.py` defines:
- Base `Building` class with `update()` and `draw()` methods
- `BUILDING_TYPES` dict mapping string IDs to classes
- Each building has production logic in `update(delta_time, inventory, ...)`

### Resource System

**5 Basic Resources** (harvestable from terrain):
- Metal (`RESOURCE_METAL`) - grey tiles
- Food (`RESOURCE_FOOD`) - dark green tiles
- Energy (`RESOURCE_ENERGY`) - orange crystals in desert
- Wood (`RESOURCE_WOOD`) - forest tiles
- Stone (`RESOURCE_STONE`) - grey stone tiles

**4 Crafted Resources** (via crafting system):
- Tools (`CRAFTING_RESOURCE_TOOLS`) - 2x harvest multiplier
- Components (`CRAFTING_RESOURCE_COMPONENTS`) - building materials
- Medicine (`CRAFTING_RESOURCE_MEDICINE`) - heals 30 HP
- Advanced Materials (`CRAFTING_RESOURCE_ADVANCED_MATERIALS`) - required for Factory

**Inventory**: Centralized dict in `player.inventory` (solo) or `game_state['inventory']` (multiplayer server)

### Enemy AI System

**3 Enemy Types**:
- **Zombie**: Standard (health: 30, speed: 1, damage: 10)
- **Mutant**: Tank (health: 60, speed: 1, damage: 15)
- **Wolf**: Fast (health: 20, speed: 1, damage: 8)

**AI Behavior** (in `enemies.py`):
1. **Wall Detection**: Enemies prioritize attacking nearby walls (50px range)
2. **Player Targeting**: Move toward player if no walls in range
3. **Attack**: Deal damage on collision (1s cooldown)
4. **Night Spawn**: 2x spawn rate during night phase

**Limitation**: Current pathfinding is direct line - no obstacle avoidance. Phase 3A will add A* pathfinding.

### Multiplayer Network Architecture

**Client-Server Model**:
- **Server Authority**: `network/server.py` maintains canonical game state
- **Client Updates**: Clients send player actions, receive state updates
- **Synchronization**: Position (10x/s), inventory, buildings, enemies

**Protocol** (JSON over TCP, port 5555):
```
MSG_CONNECT         - Player joins, receives player_id
MSG_DISCONNECT      - Player leaves
MSG_PLAYER_UPDATE   - Position/health/hunger (10x/s)
MSG_INVENTORY_UPDATE- Shared inventory changes
MSG_BUILDING_PLACE  - Building construction
MSG_BUILDING_UPDATE - Building state (durability, etc.)
MSG_ENEMY_SPAWN     - New enemy appears
MSG_ENEMY_UPDATE    - Enemy position/health
MSG_ENEMY_DEATH     - Enemy killed
MSG_GAME_STATE      - Full state sync (on connect)
MSG_HEARTBEAT       - Keep-alive (5s interval)
```

**Key Difference**: `main_multiplayer.py` has:
- `RemotePlayer` class for drawing other players (cyan squares)
- Network callbacks: `on_player_update`, `on_inventory_update`, `on_building_place`, etc.
- No save/load functionality (disabled in multiplayer)

### Procedural World Generation

`world.py` generates terrain in `__init__`:
1. **Base Layer**: All grass (`TERRAIN_GRASS`)
2. **Water**: Adds lakes (blob algorithm)
3. **Mountains**: Impassable obstacles
4. **Forests**: Wood sources (`WOOD_SOURCES_COUNT` = 10)
5. **Deserts**: Speed penalty zones with energy crystals
6. **Resources**: Scatter metal/food/stone sources

**Terrain Affects**:
- Water/Mountains: Block movement (`world.is_obstacle()`)
- Desert: 0.5x movement speed
- Forests: Harvestable for wood

### Day/Night Cycle

Implemented in `main.py`:
- **Day Duration**: `SECONDS_PER_DAY = 60` (1 minute = 1 day)
- **Day Phase**: 60% of cycle (light)
- **Night Phase**: 40% of cycle (dark blue overlay)
- **Night Effect**: Enemies spawn 2x faster (`NIGHT_ENEMY_SPAWN_MULTIPLIER`)

## Development Guidelines

### Adding a New Building

1. **Define constants** in `constants.py`:
   ```python
   BUILDING_NEWTYPE_COST = {RESOURCE_METAL: 20, ...}
   BUILDING_NEWTYPE_PRODUCTION = 5  # if applicable
   ```

2. **Create class** in `buildings.py`:
   ```python
   class NewBuilding(Building):
       def __init__(self, grid_x, grid_y):
           super().__init__('newtype', grid_x, grid_y, COLOR_YOUR_COLOR)

       def update(self, delta_time, inventory, ...):
           # Production/special logic here
   ```

3. **Register in BUILDING_TYPES** dict (buildings.py):
   ```python
   BUILDING_TYPES = {
       # ...
       'newtype': NewBuilding,
   }
   ```

4. **Add keyboard mapping** in `main.py` and `main_multiplayer.py`:
   ```python
   building_keys = {
       # ...
       pygame.K_<KEY>: 'newtype',
   }
   ```

5. **Update UI** in `ui.py`:
   - Modify `draw_building_menu()` to show new building
   - Adjust button widths if needed (current: 82px for 10 buildings)

### Adding a New Enemy Type

1. **Define constants** in `constants.py`:
   ```python
   NEWENEMY_SPAWN_INTERVAL = 20.0
   NEWENEMY_DAMAGE = 12
   NEWENEMY_SPEED = 2
   NEWENEMY_HEALTH = 40
   COLOR_NEWENEMY = (R, G, B)
   ```

2. **Create class** in `enemies.py`:
   ```python
   class NewEnemy(Enemy):
       def __init__(self, spawn_x, spawn_y):
           super().__init__(spawn_x, spawn_y, NEWENEMY_HEALTH,
                          NEWENEMY_DAMAGE, NEWENEMY_SPEED, COLOR_NEWENEMY)
   ```

3. **Add spawn function** in `enemies.py`:
   ```python
   def spawn_newenemy_randomly(world_size):
       # Return NewEnemy instance at random edge
   ```

4. **Add spawn timer** in `main.py`:
   ```python
   self.newenemy_spawn_timer = 0

   # In update loop:
   self.newenemy_spawn_timer += delta_time
   if self.newenemy_spawn_timer >= NEWENEMY_SPAWN_INTERVAL:
       enemy = spawn_newenemy_randomly(self.world.grid_size)
       self.enemies_list.append(enemy)
       self.newenemy_spawn_timer = 0
   ```

5. **Update multiplayer** sync in `main_multiplayer.py` (if applicable)

### Network Protocol Extensions

When adding new synchronized data:

1. **Define message type** in `network/protocol.py`:
   ```python
   MSG_NEW_FEATURE = "new_feature"

   class NewFeatureMessage:
       @staticmethod
       def create(param1, param2):
           data = {'param1': param1, 'param2': param2}
           return NetworkMessage.encode(MSG_NEW_FEATURE, data)
   ```

2. **Server handling** in `network/server.py`:
   - Add to `handle_client_message()`
   - Validate data
   - Update `self.game_state`
   - Broadcast to other clients

3. **Client handling** in `network/client.py`:
   - Add callback: `self.on_new_feature = None`
   - Call in `_handle_message()`

4. **Game integration** in `main_multiplayer.py`:
   - Define callback function
   - Register: `self.network_client.on_new_feature = self._on_new_feature`

### Modifying Game Balance

All balance values are in `constants.py`:
- **Economy**: Building costs, production rates (`BUILDING_*_COST`, `BUILDING_*_PRODUCTION`)
- **Combat**: Enemy stats, turret damage/range (`*_DAMAGE`, `*_HEALTH`, `TURRET_RANGE`)
- **Player**: Movement speed, hunger rate, harvest amount (`PLAYER_*`)
- **Spawning**: Enemy spawn intervals (`*_SPAWN_INTERVAL`)
- **Victory**: Days to survive, rocket cost (`SURVIVAL_DAYS_TO_WIN`, `BUILDING_ROCKET_COST`)

**Testing Balance Changes**:
1. Modify values in `constants.py`
2. Run `python main.py`
3. No recompilation needed (Python is interpreted)

## Current State & Roadmap

**Completed Phases**:
- ✅ Phase 2A-C: Buildings expansion (Wall, Warehouse, Factory)
- ✅ Phase 7B: Multiplayer online (TCP server, Hamachi support)

**Next Priorities** (see ROADMAP.md):
- Phase 3A: Pathfinding (A* algorithm for enemies)
- Phase 6A: Graphics improvements (sprites, animations, particles)
- Phase 7C: Multiplayer enhancements (chat, lobby, competitive mode)

**Known Limitations**:
- Enemies move in straight lines (no obstacle avoidance) → Phase 3A will fix
- Multiplayer save/load disabled (server authority makes this complex)
- No reconnection handling (disconnect = kicked)
- Basic placeholder graphics (colored rectangles)

## File Naming Conventions

- **Game logic**: `lowercase.py` (e.g., `player.py`, `buildings.py`)
- **Network**: `network/lowercase.py` (e.g., `network/protocol.py`)
- **Documentation**: `UPPERCASE.md` (e.g., `README.md`, `ROADMAP.md`)
- **Entry points**: `main*.py` (e.g., `main.py`, `main_multiplayer.py`, `start_server.py`)

## Testing Multiplayer Locally

**No Hamachi needed for local testing**:

1. Terminal 1 (server):
   ```bash
   python start_server.py
   # Port: 5555
   ```

2. Terminal 2 (player 1):
   ```bash
   python main_multiplayer.py
   # IP: localhost
   # Port: 5555
   ```

3. Terminal 3 (player 2):
   ```bash
   python main_multiplayer.py
   # IP: localhost
   # Port: 5555
   ```

## Git Workflow

- **Branch**: `main` (single branch development)
- **Commit style**: Descriptive messages with phase tags
  ```
  Phase 2C: Add Factory building with auto-crafting
  ```
- **Documentation updates**: CHANGELOG.md and ROADMAP.md updated with each phase

## Important Notes

- **Path Handling**: Always use full paths when referencing project directory:
  ```bash
  cd "/mnt/c/Users/ouzdi/Desktop/Frontier Forge/ForgeFrontier"
  ```

- **WSL Environment**: Project is on Windows filesystem accessed via WSL (`/mnt/c/...`)

- **Syntax Validation**: Use `python3 -m py_compile <file>` to check syntax before committing

- **Constants First**: When modifying game behavior, check `constants.py` first before touching logic code

- **Server Authority**: In multiplayer, the server (`network/server.py`) is the single source of truth. Clients should never modify game state directly, only send requests.

- **Delta Time**: All movement and timers MUST use `delta_time` parameter to ensure consistent behavior across different frame rates.
