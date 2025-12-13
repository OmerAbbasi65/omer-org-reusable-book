const fs = require('fs');
const path = require('path');

const specDir = path.join(__dirname, '../spec/chapters');
const docsDir = path.join(__dirname, '../docs');

// For now, hardcode the file name. We'll make this dynamic later.
const specFileName = '01-introduction.spec.json';
const specFilePath = path.join(specDir, specFileName);

// Ensure docs directory exists
if (!fs.existsSync(docsDir)) {
  fs.mkdirSync(docsDir, { recursive: true });
}

fs.readFile(specFilePath, 'utf8', (err, data) => {
  if (err) {
    console.error(`Error reading spec file ${specFilePath}:`, err);
    process.exit(1);
  }

  try {
    const spec = JSON.parse(data);
    let markdownContent = `# ${spec.title}\n\n`;

    spec.content.forEach(item => {
      if (item.type === 'paragraph') {
        markdownContent += `${item.text}\n\n`;
      }
    });

    const markdownFileName = `${path.basename(specFileName, '.spec.json')}.md`;
    const markdownFilePath = path.join(docsDir, markdownFileName);

    fs.writeFile(markdownFilePath, markdownContent, 'utf8', (writeErr) => {
      if (writeErr) {
        console.error(`Error writing markdown file ${markdownFilePath}:`, writeErr);
        process.exit(1);
      }
      console.log(`Successfully generated ${markdownFilePath}`);
    });
  } catch (parseErr) {
    console.error(`Error parsing JSON from ${specFilePath}:`, parseErr);
    process.exit(1);
  }
});
