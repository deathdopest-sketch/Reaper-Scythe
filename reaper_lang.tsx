import React, { useState } from 'react';
import { Skull, Users, Zap } from 'lucide-react';

export default function ReaperLanguage() {
  const [activeTab, setActiveTab] = useState('overview');

  const examples = {
    helloWorld: `# The first rising
infect Greet(soul name) {
  harvest "Greetings from the graveyard, " + name;
}

raise Greet("mortal");`,
    
    factorial: `# The reaper comes for all
infect CollectSouls(corpse n) -> corpse {
  if (n <= DEAD) {
    reap RISEN;
  }
  reap n * CollectSouls(n - RISEN);
}

corpse total = CollectSouls(5);
harvest total;  # Output: 120`,

    zombieHorde: `# Build an unstoppable horde
infect SpreadInfection(corpse days) {
  corpse horde = RISEN;
  corpse infected = RISEN;
  
  shamble day from RISEN to days {
    infected = infected * 2;  # Each zombie infects one person
    horde = horde + infected;
    harvest "Day " + day + ": " + horde + " zombies";
  }
  
  reap horde;
}

# After 7 days...
SpreadInfection(7);`,

    soulCounter: `# The reaper's tally
tomb SoulCounter {
  corpse collected = DEAD;
  corpse escaped = DEAD;
  
  infect Harvest(corpse amount) {
    this.collected = this.collected + amount;
  }
  
  infect Escape() {
    this.escaped = this.escaped + RISEN;
  }
  
  infect Total() -> corpse {
    reap this.collected - this.escaped;
  }
}

tomb reaper = spawn SoulCounter();
reaper.Harvest(100);
reaper.Escape();
harvest reaper.Total();  # 99 souls remain`,

    resurrection: `# Rise from the grave
crypt zombies = [DEAD, RISEN, 2, 3, 5];

# Animate each corpse
decay soul in zombies {
  if (soul > DEAD) {
    harvest soul + " has risen!";
  } else {
    harvest "Still dead...";
  }
}

# Eternal shambling
soulless {
  harvest "The horde shambles on forever...";
  rest 1000;  # Pause before next shamble
}`
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-green-950 to-gray-900 text-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Users className="w-12 h-12 text-green-500 animate-pulse" />
            <h1 className="text-5xl font-bold bg-gradient-to-r from-green-400 to-red-500 bg-clip-text text-transparent">
              REAPER
            </h1>
            <Zap className="w-12 h-12 text-red-500" />
          </div>
          <p className="text-xl text-green-400 italic font-semibold">
            The Undead Programming Language
          </p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-green-800">
          {['overview', 'syntax', 'examples'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-6 py-3 font-semibold capitalize transition-all ${
                activeTab === tab
                  ? 'bg-green-900 text-white border-b-2 border-green-400'
                  : 'text-green-500 hover:text-green-300'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="bg-black bg-opacity-50 rounded-lg p-6 backdrop-blur border border-green-900">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-2xl font-bold text-green-400 mb-3 flex items-center gap-2">
                  <Skull className="w-6 h-6" /> Philosophy
                </h2>
                <p className="text-gray-300 leading-relaxed">
                  Reaper is a language where code spreads like infection, functions shamble through logic, 
                  and the Grim Reaper harvests all outputs. Every program is a zombie apocalypse—variables 
                  are corpses that rise, functions infect new code, and execution is the relentless march 
                  of the undead horde.
                </p>
              </div>

              <div>
                <h2 className="text-2xl font-bold text-green-400 mb-3">Core Tenets</h2>
                <div className="grid gap-4">
                  <div className="bg-green-950 bg-opacity-50 p-4 rounded border border-green-800">
                    <h3 className="font-bold text-green-400 mb-2">🧟 Corpses (Numbers)</h3>
                    <p className="text-sm text-gray-300">Integer values that can rise from the dead</p>
                  </div>
                  <div className="bg-green-950 bg-opacity-50 p-4 rounded border border-green-800">
                    <h3 className="font-bold text-green-400 mb-2">👻 Souls (Strings)</h3>
                    <p className="text-sm text-gray-300">Text values waiting to be harvested</p>
                  </div>
                  <div className="bg-green-950 bg-opacity-50 p-4 rounded border border-green-800">
                    <h3 className="font-bold text-green-400 mb-2">🦠 Infect (Functions)</h3>
                    <p className="text-sm text-gray-300">Spread your logic like a zombie virus</p>
                  </div>
                  <div className="bg-green-950 bg-opacity-50 p-4 rounded border border-green-800">
                    <h3 className="font-bold text-green-400 mb-2">⚰️ Harvest (Output)</h3>
                    <p className="text-sm text-gray-300">The reaper collects and displays values</p>
                  </div>
                  <div className="bg-green-950 bg-opacity-50 p-4 rounded border border-green-800">
                    <h3 className="font-bold text-green-400 mb-2">🚶 Shamble (Loops)</h3>
                    <p className="text-sm text-gray-300">The slow, inevitable march of iteration</p>
                  </div>
                  <div className="bg-green-950 bg-opacity-50 p-4 rounded border border-green-800">
                    <h3 className="font-bold text-green-400 mb-2">🪦 Tomb (Classes)</h3>
                    <p className="text-sm text-gray-300">Resting places that hold multiple corpses and souls</p>
                  </div>
                </div>
              </div>

              <div className="bg-red-950 bg-opacity-30 p-4 rounded border border-red-800">
                <h3 className="font-bold text-red-400 mb-2">⚠️ The Reaper's Law</h3>
                <p className="text-sm text-gray-300">
                  All functions must eventually <span className="text-red-400 font-mono">reap</span> (return) or 
                  <span className="text-green-400 font-mono"> harvest</span> (output). The reaper always collects what is due.
                </p>
              </div>
            </div>
          )}

          {activeTab === 'syntax' && (
            <div className="space-y-4">
              <h2 className="text-2xl font-bold text-green-400 mb-4">Syntax Guide</h2>
              
              <div className="space-y-4 font-mono text-sm">
                <div className="bg-gray-950 p-4 rounded border border-green-800">
                  <div className="text-green-500 mb-2"># Variable Declaration</div>
                  <div className="text-lime-300">corpse zombies = 10;</div>
                  <div className="text-lime-300">soul message = "Braaaaains";</div>
                  <div className="text-lime-300">crypt horde = [1, 2, 3, 5, 8];</div>
                  <div className="text-gray-500 mt-2"># DEAD = 0, RISEN = 1 (built-in constants)</div>
                </div>

                <div className="bg-gray-950 p-4 rounded border border-green-800">
                  <div className="text-green-500 mb-2"># Function Definition</div>
                  <div className="text-lime-300">infect Bite(corpse victim) -> corpse {'{'}</div>
                  <div className="text-lime-300 ml-4">reap victim + RISEN;  # Return value</div>
                  <div className="text-lime-300">{'}'}</div>
                  <div className="text-gray-500 mt-2"># Call with: raise Bite(5);</div>
                </div>

                <div className="bg-gray-950 p-4 rounded border border-green-800">
                  <div className="text-green-500 mb-2"># Loops</div>
                  <div className="text-lime-300">shamble i from RISEN to 10 {'{'}</div>
                  <div className="text-lime-300 ml-4">harvest i;</div>
                  <div className="text-lime-300">{'}'}</div>
                  <div className="text-lime-300 mt-3">decay item in horde {'{'}</div>
                  <div className="text-lime-300 ml-4">harvest item;</div>
                  <div className="text-lime-300">{'}'}</div>
                  <div className="text-lime-300 mt-3">soulless {'{'}</div>
                  <div className="text-lime-300 ml-4"># Infinite loop - shambles forever</div>
                  <div className="text-lime-300">{'}'}</div>
                </div>

                <div className="bg-gray-950 p-4 rounded border border-green-800">
                  <div className="text-green-500 mb-2"># Classes (Tombs)</div>
                  <div className="text-lime-300">tomb Zombie {'{'}</div>
                  <div className="text-lime-300 ml-4">corpse hunger = 100;</div>
                  <div className="text-lime-300 ml-4">soul moan;</div>
                  <div className="text-lime-300 ml-4"></div>
                  <div className="text-lime-300 ml-4">infect Feed() {'{'}</div>
                  <div className="text-lime-300 ml-8">this.hunger = this.hunger - 10;</div>
                  <div className="text-lime-300 ml-4">{'}'}</div>
                  <div className="text-lime-300">{'}'}</div>
                  <div className="text-lime-300 mt-2">tomb z = spawn Zombie();</div>
                </div>

                <div className="bg-gray-950 p-4 rounded border border-green-800">
                  <div className="text-green-500 mb-2"># Conditionals</div>
                  <div className="text-lime-300">if (hunger > 50) {'{'}</div>
                  <div className="text-lime-300 ml-4">harvest "Hungry...";</div>
                  <div className="text-lime-300">{'}'} otherwise {'{'}</div>
                  <div className="text-lime-300 ml-4">harvest "Satisfied";</div>
                  <div className="text-lime-300">{'}'}</div>
                </div>

                <div className="bg-gray-950 p-4 rounded border border-green-800">
                  <div className="text-green-500 mb-2"># Comments</div>
                  <div className="text-lime-300"># Single line epitaph</div>
                  <div className="text-lime-300 mt-2">## Multi-line</div>
                  <div className="text-lime-300">## tombstone inscription ##</div>
                </div>
              </div>

              <div className="mt-6 p-4 bg-green-950 bg-opacity-30 rounded border border-green-800">
                <h3 className="font-bold text-green-400 mb-2">Reserved Words</h3>
                <div className="grid grid-cols-3 gap-2 text-sm">
                  <div><span className="text-lime-300">DEAD</span> = 0</div>
                  <div><span className="text-lime-300">RISEN</span> = 1</div>
                  <div><span className="text-lime-300">harvest</span> (print)</div>
                  <div><span className="text-lime-300">reap</span> (return)</div>
                  <div><span className="text-lime-300">raise</span> (call)</div>
                  <div><span className="text-lime-300">rest</span> (sleep)</div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'examples' && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-green-400 mb-4">Code Examples</h2>
              
              {Object.entries(examples).map(([key, code]) => (
                <div key={key} className="bg-gray-950 rounded border border-green-800">
                  <div className="bg-green-950 bg-opacity-50 px-4 py-2 font-semibold capitalize border-b border-green-800 text-green-300">
                    {key.replace(/([A-Z])/g, ' $1').trim()}
                  </div>
                  <pre className="p-4 overflow-x-auto text-sm">
                    <code className="text-lime-300">{code}</code>
                  </pre>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-green-500 italic text-sm flex items-center justify-center gap-2">
          <Skull className="w-4 h-4" />
          <span>"The code rises. The horde shambles. The reaper harvests all."</span>
          <Skull className="w-4 h-4" />
        </div>
      </div>
    </div>
  );
}