import './App.css';
import React, { useEffect, useState, useRef } from 'react';
import io from 'socket.io-client';

function ProgressBar({ value, max = 100 }) {
  var percentage = Math.min((value / max) * 100, 100);
  
  return (
    <div style={{
      height: '60px',
      width: '70%',
      backgroundColor: '#EDE8F5',
      overflow: 'hidden',
      boxShadow: "1px 7px 15px .5px black",
    }}>
    
      <div style={{
        height: '100%',
        width: `${percentage}%`,
        backgroundColor: '#7091E6',
        transition: 'width 0.4s ease-in-out',
      }} />
    </div>
  );
}

function App() {
  const [showNav, setShowNav] = useState(true);
  const [lastScrollY, setLastScrollY] = useState(0);
  const [score, setScore] = useState(null);
  const socketRef = useRef(null);
  const scrollRef = useRef(null);
  useEffect(() => {
    socketRef.current = io('http://localhost:8468');

    socketRef.current.on("connect", () => {
      console.log("Connected:", socketRef.current.id);
    });

    socketRef.current.on("postureScore", (newScore) => {
      console.log("New postureScore:", newScore);
      newScore = Math.round(newScore)
      if (newScore > 100){
        newScore = 100;
      }
      if (newScore < 0){
        newScore = 0;
      }
      setScore(newScore);
    });

    return () => {
      socketRef.current.disconnect();
    };
  }, []);

  useEffect(() => {
    let timeoutId = null;

    const handleScroll = () => {
      if (timeoutId) return;
      timeoutId = setTimeout(() => {
        const currentY = window.scrollY;
        if (currentY > lastScrollY && currentY > 50) {
          setShowNav(false);
        } else {
          setShowNav(true);
        }
        setLastScrollY(currentY);
        timeoutId = null;
      }, 500);
    };

    const handleMouseMove = (e) => {
      if (e.clientY < 100) {
        setShowNav(true);
      }
    };

    window.addEventListener('scroll', handleScroll);
    window.addEventListener('mousemove', handleMouseMove);

    return () => {
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, [lastScrollY]);

  return (
    <div className="App">
      <div className={`navbar ${showNav ? 'visible' : 'hidden'}`}>
        <div>EVIL POSTURE CORRECTOR</div>
      </div>
      <section>
      <div className="gif">
      
      <img src="http://localhost:6864/video_feed" width="640" height="480" />
      <img src="./please.gif"></img>
      </div>
      </section>
      <section>
      <div className="live-score">
        <div className='live-text'>Live Posture Score: {score !== null ? score : "Waiting..."}</div>
        <div className='progress-bar'><ProgressBar value={score || 0} /></div>
      </div>
      </section>
      <section className="testimonials-section">
  <div className="testimonials-container">
    <h2>Victims of Good Posture</h2>
    <div className="testimonial">
      <p>“I slouched once. It slapped me so hard I’m now permanently aligned with the Earth's magnetic field.”</p>
      <span>- Chad S., Former Gamer</span>
    </div>
    <div className="testimonial">
      <p>“It caught me mid-slump in a Zoom call. My coworkers now think I was mugged by a ghost.”</p>
      <span>- Linda B., Remote Worker</span>
    </div>
    <div className="testimonial">
      <p>“My chiropractor cried tears of joy. 10/10, would get pool-noodled again.”</p>
      <span>- Ravi T., Recovering Hunchback</span>
    </div>
    <div className="testimonial">
      <p>“I’m scared to sit. I’m writing this review while standing on a yoga ball.”</p>
      <span>- Anonymous, Traumatized but Upright</span>
    </div>
  </div>
</section>

    </div>
  );
}

export default App;
