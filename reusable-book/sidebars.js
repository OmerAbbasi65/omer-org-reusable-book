// @ts-check

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.

 @type {import('@docusaurus/plugin-content-docs').SidebarsConfig}
 */
const sidebars = {
  // Manually defined sidebar with book chapters
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Book Chapters',
      collapsed: false,
      items: [
        '01-introduction',
        '02-module1-ros2',
        '03-module2-digital-twin',
        '04-module3-nvidia-isaac',
        '05-module4-vla',
      ],
    },
    {
      type: 'category',
      label: 'Tutorial Basics',
      collapsed: true,
      items: [
        'tutorial-basics/create-a-document',
        'tutorial-basics/create-a-blog-post',
        'tutorial-basics/create-a-page',
        'tutorial-basics/markdown-features',
        'tutorial-basics/deploy-your-site',
        'tutorial-basics/congratulations',
      ],
    },
    {
      type: 'category',
      label: 'Tutorial Extras',
      collapsed: true,
      items: [
        'tutorial-extras/manage-docs-versions',
        'tutorial-extras/translate-your-site',
      ],
    },
  ],
};

export default sidebars;
