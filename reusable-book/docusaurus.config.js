// @ts-check
// PLEASE FILL IN THE FOLLOWING VALUES FOR GITHUB PAGES DEPLOYMENT
// organizationName: 'YOUR_GITHUB_ORGANIZATION_NAME', 
// projectName: 'YOUR_GITHUB_REPOSITORY_NAME',

// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).
// There are various equivalent ways to declare your Docusaurus config.
// See: https://docusaurus.io/docs/api/docusaurus-config

import {themes as prismThemes} from 'prism-react-renderer';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'An AI-driven book on robotics and artificial intelligence',
  favicon: 'img/favicon.ico',

  // Custom fields for environment variables accessible in client-side code
  customFields: {
    backendUrl: process.env.BACKEND_URL || 'https://joseph8071-robotics-rag-backend.hf.space',
  },

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: 'https://omer-org-reusable-book.vercel.app',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For Vercel deployment, use root path
  baseUrl: '/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'OmerAbbasi65', // Your GitHub username
  projectName: 'omer-org-reusable-book', // Your repository name

  onBrokenLinks: 'throw',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          // editUrl: 'https://github.com/OmerAbbasi65/omer-org-reusable-book',
        },
        blog: {
          showReadingTime: true,
          feedOptions: {
            type: ['rss', 'atom'],
            xslt: true,
          },
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          // editUrl: 'https://github.com/OmerAbbasi65/omer-org-reusable-book',
          // Useful options to enforce blogging best practices
          onInlineTags: 'warn',
          onInlineAuthors: 'warn',
          onUntruncatedBlogPosts: 'warn',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      image: 'img/docusaurus-social-card.jpg',
      colorMode: {
        respectPrefersColorScheme: true,
      },
      navbar: {
        title: 'Physical AI & Humanoid Robotics',
        logo: {
          alt: 'Physical AI & Humanoid Robotics Logo',
          src: 'img/logo.svg',
        },
        hideOnScroll: false,
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'Chapters',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Book Chapters',
            items: [
              {
                label: 'Introduction to the Unified Book Project',
                to: '/docs/01-introduction',
              },
              {
                label: 'The Robotic Nervous System (ROS 2)',
                to: '/docs/02-module1-ros2',
              },
              {
                label: 'The Digital Twin (Gazebo & Unity)',
                to: '/docs/03-module2-digital-twin',
              },
              {
                label: 'The AI-Robot Brain (NVIDIA Isaac)',
                to: '/docs/04-module3-nvidia-isaac',
              },
              {
                label: 'Vision-Language-Action (VLA)',
                to: '/docs/05-module4-vla',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Physical AI & Humanoid Robotics.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
      },
    }),
};

export default config;
