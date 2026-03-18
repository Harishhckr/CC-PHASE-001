# DJ Claude

A professional web-based DJ music mixing application with dual decks, crossfader, and real-time audio controls.

## Features

- **Dual Deck System**: Load and play tracks on two independent decks (Deck A and Deck B)
- **Crossfader**: Smooth transitions between decks with professional crossfading
- **Volume Control**: Independent volume control for each deck plus master volume
- **Playback Speed Control**: Adjust playback speed from 50% to 150% for beatmatching
- **Audio Effects Panel**: Bass boost, treble, and echo effects
- **Responsive Design**: Works on desktop and mobile devices
- **Modern UI**: Beautiful gradient interface with glassmorphism effects

## Installation

1. Install dependencies:
```bash
npm install
```

2. Start the server:
```bash
npm start
```

3. Open your browser and navigate to:
```
http://localhost:3000
```

## Development

Run the application in development mode with auto-reload:
```bash
npm run dev
```

## Usage

1. **Load Tracks**: Click the file input on Deck A or Deck B to load audio files
2. **Play/Pause**: Use the built-in audio controls to play or pause tracks
3. **Mix Tracks**: Use the crossfader to blend between Deck A and Deck B
4. **Adjust Speed**: Change playback speed to match beats between tracks
5. **Control Volume**: Adjust individual deck volumes and master volume
6. **Apply Effects**: Use the effects panel to enhance your mix

## Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Backend**: Node.js, Express
- **Audio**: Web Audio API, HTML5 Audio Elements

## Browser Support

Works best in modern browsers with full Web Audio API support:
- Chrome 80+
- Firefox 75+
- Safari 14+
- Edge 80+

## License

MIT
