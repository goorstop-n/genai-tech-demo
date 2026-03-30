// Snake Game JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Game variables
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    const scoreElement = document.getElementById('score');
    const highScoreElement = document.getElementById('high-score');
    const startBtn = document.getElementById('startBtn');
    const pauseBtn = document.getElementById('pauseBtn');
    const resetBtn = document.getElementById('resetBtn');
    
    // Game constants
    const GRID_SIZE = 20;
    const CANVAS_WIDTH = canvas.width;
    const CANVAS_HEIGHT = canvas.height;
    
    // Game state
    let snake = [];
    let food = {};
    let direction = 'right';
    let nextDirection = 'right';
    let gameSpeed = 100; // ms
    let gameInterval;
    let score = 0;
    let highScore = localStorage.getItem('snakeHighScore') || 0;
    let isPaused = false;
    let gameStarted = false;
    
    // Initialize game
    function initGame() {
        // Initialize snake
        snake = [
            {x: 10 * GRID_SIZE, y: 10 * GRID_SIZE},
            {x: 9 * GRID_SIZE, y: 10 * GRID_SIZE},
            {x: 8 * GRID_SIZE, y: 10 * GRID_SIZE}
        ];
        
        // Generate first food
        generateFood();
        
        // Reset score
        score = 0;
        scoreElement.textContent = score;
        highScoreElement.textContent = highScore;
        
        // Reset direction
        direction = 'right';
        nextDirection = 'right';
        
        // Draw initial state
        draw();
    }
    
    // Generate food at random position
    function generateFood() {
        // Ensure food doesn't appear on snake
        let foodOnSnake;
        do {
            foodOnSnake = false;
            food = {
                x: Math.floor(Math.random() * (CANVAS_WIDTH / GRID_SIZE)) * GRID_SIZE,
                y: Math.floor(Math.random() * (CANVAS_HEIGHT / GRID_SIZE)) * GRID_SIZE
            };
            
            // Check if food overlaps with snake
            for (let segment of snake) {
                if (segment.x === food.x && segment.y === food.y) {
                    foodOnSnake = true;
                    break;
                }
            }
        } while (foodOnSnake);
    }
    
    // Draw everything
    function draw() {
        // Clear canvas
        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
        
        // Draw snake
        snake.forEach((segment, index) => {
            if (index === 0) {
                // Snake head
                ctx.fillStyle = '#0fce7c';
                ctx.fillRect(segment.x, segment.y, GRID_SIZE, GRID_SIZE);
                
                // Draw eyes
                ctx.fillStyle = '#000';
                const eyeSize = GRID_SIZE / 5;
                const offset = GRID_SIZE / 3;
                
                if (direction === 'right') {
                    ctx.fillRect(segment.x + GRID_SIZE - offset, segment.y + offset, eyeSize, eyeSize);
                    ctx.fillRect(segment.x + GRID_SIZE - offset, segment.y + GRID_SIZE - offset - eyeSize, eyeSize, eyeSize);
                } else if (direction === 'left') {
                    ctx.fillRect(segment.x + offset - eyeSize, segment.y + offset, eyeSize, eyeSize);
                    ctx.fillRect(segment.x + offset - eyeSize, segment.y + GRID_SIZE - offset - eyeSize, eyeSize, eyeSize);
                } else if (direction === 'up') {
                    ctx.fillRect(segment.x + offset, segment.y + offset - eyeSize, eyeSize, eyeSize);
                    ctx.fillRect(segment.x + GRID_SIZE - offset - eyeSize, segment.y + offset - eyeSize, eyeSize, eyeSize);
                } else if (direction === 'down') {
                    ctx.fillRect(segment.x + offset, segment.y + GRID_SIZE - offset, eyeSize, eyeSize);
                    ctx.fillRect(segment.x + GRID_SIZE - offset - eyeSize, segment.y + GRID_SIZE - offset, eyeSize, eyeSize);
                }
            } else {
                // Snake body
                ctx.fillStyle = '#4cd964';
                ctx.fillRect(segment.x, segment.y, GRID_SIZE, GRID_SIZE);
                
                // Body pattern
                ctx.fillStyle = '#0a9e5c';
                ctx.fillRect(segment.x + 5, segment.y + 5, GRID_SIZE - 10, GRID_SIZE - 10);
            }
        });
        
        // Draw food
        ctx.fillStyle = '#ff3b30';
        ctx.beginPath();
        ctx.arc(
            food.x + GRID_SIZE / 2,
            food.y + GRID_SIZE / 2,
            GRID_SIZE / 2,
            0,
            Math.PI * 2
        );
        ctx.fill();
        
        // Draw food highlight
        ctx.fillStyle = '#ffcc00';
        ctx.beginPath();
        ctx.arc(
            food.x + GRID_SIZE / 2 - 3,
            food.y + GRID_SIZE / 2 - 3,
            GRID_SIZE / 6,
            0,
            Math.PI * 2
        );
        ctx.fill();
    }
    
    // Update game state
    function update() {
        // Update direction
        direction = nextDirection;
        
        // Calculate new head position
        const head = {...snake[0]};
        
        switch(direction) {
            case 'up':
                head.y -= GRID_SIZE;
                break;
            case 'down':
                head.y += GRID_SIZE;
                break;
            case 'left':
                head.x -= GRID_SIZE;
                break;
            case 'right':
                head.x += GRID_SIZE;
                break;
        }
        
        // Check wall collision
        if (
            head.x < 0 || 
            head.x >= CANVAS_WIDTH || 
            head.y < 0 || 
            head.y >= CANVAS_HEIGHT
        ) {
            gameOver();
            return;
        }
        
        // Check self collision
        for (let segment of snake) {
            if (head.x === segment.x && head.y === segment.y) {
                gameOver();
                return;
            }
        }
        
        // Add new head to snake
        snake.unshift(head);
        
        // Check food collision
        if (head.x === food.x && head.y === food.y) {
            // Increase score
            score += 10;
            scoreElement.textContent = score;
            
            // Update high score
            if (score > highScore) {
                highScore = score;
                highScoreElement.textContent = highScore;
                localStorage.setItem('snakeHighScore', highScore);
            }
            
            // Generate new food
            generateFood();
            
            // Increase speed slightly (cap at minimum speed)
            if (gameSpeed > 50) {
                gameSpeed -= 1;
                clearInterval(gameInterval);
                gameInterval = setInterval(gameLoop, gameSpeed);
            }
        } else {
            // Remove tail if no food eaten
            snake.pop();
        }
        
        // Draw updated game
        draw();
    }
    
    // Main game loop
    function gameLoop() {
        if (!isPaused && gameStarted) {
            update();
        }
    }
    
    // Game over function
    function gameOver() {
        gameStarted = false;
        clearInterval(gameInterval);
        
        // Display game over message
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
        
        ctx.fillStyle = '#ff3b30';
        ctx.font = 'bold 48px "Press Start 2P", cursive';
        ctx.textAlign = 'center';
        ctx.fillText('GAME OVER', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 - 30);
        
        ctx.fillStyle = '#fff';
        ctx.font = '24px Arial';
        ctx.fillText(`Score: ${score}`, CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 + 30);
        
        if (score === highScore && score > 0) {
            ctx.fillStyle = '#ffcc00';
            ctx.fillText('NEW HIGH SCORE!', CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2 + 70);
        }
        
        startBtn.textContent = 'Restart Game';
    }
    
    // Start game function
    function startGame() {
        if (!gameStarted) {
            gameStarted = true;
            isPaused = false;
            pauseBtn.textContent = 'Pause';
            initGame();
            gameInterval = setInterval(gameLoop, gameSpeed);
        }
    }
    
    // Toggle pause function
    function togglePause() {
        if (!gameStarted) return;
        
        isPaused = !isPaused;
        pauseBtn.textContent = isPaused ? 'Resume' : 'Pause';
        
        if (!isPaused) {
            draw();
        }
    }
    
    // Reset game function
    function resetGame() {
        gameStarted = false;
        isPaused = false;
        clearInterval(gameInterval);
        gameSpeed = 100;
        startBtn.textContent = 'Start Game';
        pauseBtn.textContent = 'Pause';
        initGame();
    }
    
    // Keyboard controls
    document.addEventListener('keydown', function(event) {
        if (!gameStarted) return;
        
        switch(event.key) {
            case 'ArrowUp':
            case 'w':
            case 'W':
                if (direction !== 'down') nextDirection = 'up';
                break;
            case 'ArrowDown':
            case 's':
            case 'S':
                if (direction !== 'up') nextDirection = 'down';
                break;
            case 'ArrowLeft':
            case 'a':
            case 'A':
                if (direction !== 'right') nextDirection = 'left';
                break;
            case 'ArrowRight':
            case 'd':
            case 'D':
                if (direction !== 'left') nextDirection = 'right';
                break;
            case 'p':
            case 'P':
                togglePause();
                break;
        }
    });
    
    // Button event listeners
    startBtn.addEventListener('click', startGame);
    pauseBtn.addEventListener('click', togglePause);
    resetBtn.addEventListener('click', resetGame);
    
    // Initialize game on load
    initGame();
    
    // Instructions for mobile users
    console.log('Snake Game Loaded!');
    console.log('Controls: Arrow Keys or WASD');
    console.log('Press P to pause/resume');
});