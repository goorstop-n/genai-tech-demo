# Web Snake Game

A classic Snake game implemented using HTML5, CSS3, and JavaScript.

## Features

- Classic snake gameplay with smooth controls
- Score tracking and high score persistence (using localStorage)
- Responsive design that works on desktop and mobile
- Attractive retro-style UI with animations
- Keyboard controls (Arrow keys or WASD)
- Pause/Resume functionality

## How to Play

1. Open `index.html` in a modern web browser
2. Click "Start Game" button
3. Use **Arrow Keys** or **WASD** to control the snake
4. Eat the red food to grow and increase your score
5. Avoid hitting the walls or your own tail
6. Press **P** to pause/resume the game

## Files

- `index.html` - Main HTML file
- `style.css` - CSS styles for the game
- `script.js` - JavaScript game logic

## Running Locally

### Method 1: Direct file opening
Simply open `index.html` in your web browser.

### Method 2: Using a local server
For better compatibility (especially with localStorage), you can run a local server:

```bash
# Using Python 3
cd snake
python3 -m http.server 8000
```

Then open http://localhost:8000 in your browser.

### Method 3: Using Node.js
```bash
cd snake
npx serve
```

## Game Rules

- The snake grows by one segment each time it eats food
- Each food item gives 10 points
- The game speeds up slightly as you score more points
- Game ends when snake hits a wall or itself
- High score is saved in your browser's localStorage

## Controls

- **Arrow Keys** or **WASD** - Change snake direction
- **P** - Pause/Resume game
- **Start Game** - Start or restart game
- **Pause** - Pause the game
- **Reset** - Reset game to initial state

## Browser Compatibility

The game works on all modern browsers including:
- Chrome
- Firefox
- Safari
- Edge

## Credits

Created as a web development project.

## License

This project is open source and available for educational purposes.