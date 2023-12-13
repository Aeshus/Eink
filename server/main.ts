const fs = require('fs');

function display(str: string): Promise<void> {
  return new Promise((resolve) => {
    console.log(str);
    resolve();
  })
}

interface Task {
  start(): Promise<void>;
  end(): Promise<void>;
}

class ImageTask implements Task {
  image: File;

  constructor(image: File) {
    this.image = image;
  }

  start(): Promise<void> {
    const formData = new FormData();
    formData.append('image', new Blob([this.image], { type: "image/png"}));
    console.log(formData);

    return (fetch('http://localhost:8000/upload', {
      method: 'POST',
      body: formData,
    }).then(_response => { return; }));
  }

  end(): Promise<void> {
    return display(`ending ${this.image.name}`);
  }
}

class TextTask implements Task {
  text: string;

  constructor(text: string) {
    this.text = text;
  }

  start(): Promise<void> {
    const formData = new FormData();
    formData.append('text', new Blob([this.text], { type: "text/plain"}));
    console.log(formData);

    return (fetch('http://localhost:8000/write', {
      method: 'POST',
      body: formData,
    }).then(_response => { return; }));
  }

  end(): Promise<void> {
    return display(`ending ${this.text}`);
  }
}


class DurationTask implements Task {
  tasks: Array<[Task, number]>;
  currentTask: Task | null = null;
  stopped: boolean = false;

  constructor(...tasks: Array<[Task, number]>) {
    this.tasks = tasks;
  }

  async start(): Promise<void> {
    display("starting duration")
    this.stopped = false;
    this.run();
  }

  private async run(index: number = 0): Promise<void> {
    if (this.stopped) return Promise.resolve();

    const [currentTask, duration] = this.tasks.at(index)!;
    this.currentTask = currentTask;

    await currentTask.start();

    await new Promise((resolve) => setTimeout(resolve, duration));

    if (!this.stopped) {
      await currentTask.end();
    }

    this.currentTask = null;
    
    if (!this.stopped) {
      this.run((index + 1) % this.tasks.length);
    }
  }

  async end(): Promise<void> {
    this.stopped = true;

    if (this.currentTask) {
      await this.currentTask.end();
    }

    display('ending duration')
  }
}

const a = new DurationTask(
  [new ImageTask(fs.readFileSync('./bird.png')), 5000],
  [new TextTask("Heya!"), 5000],
);

a.start().catch(console.error);
