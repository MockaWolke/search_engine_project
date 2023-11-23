let CANVAS_WIDTH = 0;
let CANVAS_HEIGHT = 0;
let VECTOR_BOX = 20;
let N_PARTICLES = 2000;
let SPAWN_BUFFER = 10;
let STEPSIZE = 3;
let MOMENTUM = 0.98;
let NOISE_SCALE = 2;
let STEPS = 0;

let vectors = new Map();
let particles = [];

if (VECTOR_BOX % 2 != 0) {
  console.error("VECTOR_BOX must be even");
}

function findClosestKey(particle) {
  let x_key;
  let y_key;
  rest_x = particle.x % VECTOR_BOX;
  rest_y = particle.y % VECTOR_BOX;

  x_key = (Math.floor(particle.x / VECTOR_BOX) + 0.5) * VECTOR_BOX;
  y_key = (Math.floor(particle.y / VECTOR_BOX) + 0.5) * VECTOR_BOX;

  return `${x_key},${y_key}`;
}

function getRandomFloatInRange(min, max) {
  let num = Math.random() * (max - min) + min;
  return Math.round(num * 100) / 100;
}

function normalize(vector, to_length = 1) {
  const norm = Math.sqrt(vector.reduce((sum, val) => sum + val * val, 0));
  if (norm === 0) {
    return vector.map((val) => 0);
  }
  return vector.map((val) => (val / norm) * to_length);
}

function castStringToArray(s) {
  return s.split(",").map(parseFloat);
}

function noiseVec(x, y, strength = 1, noiseScale = 0.01) {
  digit = noise(x * noiseScale, y * noiseScale);

  return [
    Math.cos(digit * 2 * Math.PI) * strength,
    Math.sin(digit * 2 * Math.PI) * strength,
  ];
}
const startTime = Date.now() / 1000;

function setup() {
  noiseSeed(2);

  CANVAS_WIDTH = windowWidth + (VECTOR_BOX - (windowWidth % VECTOR_BOX));
  CANVAS_HEIGHT = windowHeight + (VECTOR_BOX - (windowHeight % VECTOR_BOX));

  let myCanvas = createCanvas(windowWidth, windowHeight);
  myCanvas.parent("myContainer");
  background(0);
  frameRate(120);

  for (let x = VECTOR_BOX / 2; x < CANVAS_WIDTH; x += VECTOR_BOX) {
    for (let y = VECTOR_BOX / 2; y < CANVAS_HEIGHT; y += VECTOR_BOX) {
      var vec = noiseVec(x, y, (noiseScale = NOISE_SCALE));

      vectors.set(`${x},${y}`, vec);
    }
  }

  stroke(139, 0, 0);
  // for (let x = VECTOR_BOX; x < CANVAS_WIDTH; x += VECTOR_BOX) {
  //   line(x, 0, x, CANVAS_HEIGHT);
  // }

  // for (let y = VECTOR_BOX; y < CANVAS_HEIGHT; y += VECTOR_BOX) {
  //   line(0, y, CANVAS_WIDTH, y);
  // }

  // for (let [key, value] of vectors.entries()) {
  //   const [x, y] = castStringToArray(key);

  //   line(x, y, x + value[0] * 5, y + value[1] * 5);
  // }

  for (let i = 0; i < N_PARTICLES; i += 1) {
    particles.push({
      x: getRandomFloatInRange(SPAWN_BUFFER, CANVAS_WIDTH - SPAWN_BUFFER),
      y: getRandomFloatInRange(SPAWN_BUFFER, CANVAS_HEIGHT - SPAWN_BUFFER),
      momentumX: 0.5,
      momentumY: -0.5,
    });
  }

  //   for (let { x, y, momentumX, momentumY } of particles) {
  //     ellipse(x, y, 3, 3);
  //   }
}

function draw() {
  //   background(255);
  fill(255, 255, 255, 20); // Set the fill to black with alpha of 10
  stroke(255, 255, 255, 20);
  strokeWeight(1);
  for (let particle of particles) {
    closest_key = findClosestKey(particle);
    if (!vectors.has(closest_key)) {
      console.log("Vector Not found", particle, closest_key);
      process.exit(1);
    }
    let vector_ms = vectors.get(closest_key);
    particle.momentumX =
      particle.momentumX * MOMENTUM + (1 - MOMENTUM) * vector_ms[0];
    particle.momentumY =
      particle.momentumY * MOMENTUM + (1 - MOMENTUM) * vector_ms[1];
    new_x = particle.x + particle.momentumX * STEPSIZE;
    new_y = particle.y + particle.momentumY * STEPSIZE;
    line(particle.x, particle.y, new_x, new_y);
    particle.x = (new_x + CANVAS_WIDTH) % CANVAS_WIDTH;
    particle.y = (new_y + CANVAS_HEIGHT) % CANVAS_HEIGHT;
  }
  if (STEPS % 10 == 0) {
    for (let x = VECTOR_BOX / 2; x < CANVAS_WIDTH; x += VECTOR_BOX) {
      for (let y = VECTOR_BOX / 2; y < CANVAS_HEIGHT; y += VECTOR_BOX) {
        time_diff = (Date.now() / 1000 - startTime) * 20;
        var vec = noiseVec(
          x + time_diff,
          y + time_diff,
          (noiseScale = NOISE_SCALE)
        ); // Use a new noise scale or some other way to generate different values
        // Update the value for the key in the map
        vectors.set(`${x},${y}`, vec);
      }
    }
  }
  STEPS += 1;
  //   MOMENTUM += (1 - MOMENTUM) * 0.004;
  //   console.log(MOMENTUM);
}
