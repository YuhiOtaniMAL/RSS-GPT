# RSS-GPT

[![](https://img.shields.io/github/last-commit/yinan-c/RSS-GPT/main?label=feeds%20refreshed)](https://yinan-c.github.io/RSS-GPT/)
[![](https://img.shields.io/github/license/yinan-c/RSS-GPT)](https://github.com/yinan-c/RSS-GPT/blob/master/LICENSE)

The workflow is still valid to use (using your own fork), but feeds update in this repo is suspended for now.
If you need a web GUI to manage feeds better, check out my latest project: [RSSBrew](https://github.com/yinan-c/RSSBrew), a self-hosted RSS-GPT alternative with more features and customizability, built with Django.

## What is this?

[Configuration Guide](https://yinan-c.github.io/rss-gpt-manual-en.html) | [中文简介](README-zh.md) | [中文教程](https://yinan-c.github.io/rss-gpt-manual-zh.html)

Using GitHub Actions to run a simple Python script repeatedly: Calling OpenAI API to generate summaries for RSS feeds, and push the generated feeds to GitHub Pages. Easy to configure, no server needed.

### Features

- Use ChatGPT to summarize RSS feeds, and attach summaries to the original articles, support custom summary length and target language.
- Aggregate multiple RSS feeds into one, remove duplicate articles, subscribe with a single address.
- Add filters to your own personalized RSS feeds.
- Host your own RSS feeds on GitHub repo and GitHub Pages.

![](https://i.imgur.com/7darABv.jpg)

## Quick configuration guide

- Fork this repo
- Add Repository Secrets
    - U_NAME: your GitHub username
    - U_EMAIL: your GitHub email
    - WORK_TOKEN: your GitHub personal access token with `repo` and `workflow` scope, get it from [GitHub settings](https://github.com/settings/tokens/new)
    - OPENAI_API_KEY(OPTIONAL, only needed when using AI summarization feature): Get it from [OpenAI website](https://platform.openai.com/account/api-keys)
- Enable GitHub Pages in repo settings, choose deploy from branch, and set the directory to `/docs`.
- Configure your RSS feeds in config.ini

You can check out [here](https://yinan-c.github.io/rss-gpt-manual-en.html) for a more detailed configuration guide.

## ChangeLog and updates

- As OpenAI released a new version of `openai` package on Nov 06, 2023.  [More powerful models are coming](https://openai.com/blog/new-models-and-developer-products-announced-at-devday), the way to call API also changed. As a result, the old script will no longer work with the latest version installed, and needs to be updated. Otherwise, you will have to set `openai==0.27.8` in `requirements.txt` to use the old version.
- Check out the [CHANGELOG.md](CHANGELOG.md).

### Contributions are welcome!

- Feel free to submit issues and pull requests.

## Support this project

- If you find it helpful, please star this repo. Please also consider buying me a coffee to help maintain this project and cover the expenses of OpenAI API while hosting the feeds. I appreciate your support.

<a href="https://www.buymeacoffee.com/yinan" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

## Example feeds being processed

These feeds on hosted in the [`docs/` subdirectory](https://github.com/yinan-c/RSS-GPT/tree/main/docs) in this repo as well as on my [GitHub Pages](https://yinan-c.github.io/RSS-GPT/). Feel free to subscribe in your favorite RSS reader.

I will consider hosting more feeds in the future. Email me or submit an issue if there are any questions using the script or any suggestions.

- https://github.com/vercel/next.js/releases.atom, https://github.com/nestjs/nest/releases.atom, https://github.com/prisma/prisma/releases.atom, https://github.com/facebook/react/releases.atom, https://github.com/hashicorp/terraform/releases.atom, https://github.com/aws/aws-cdk/releases.atom, https://aws.amazon.com/about-aws/whats-new/recent/feed/, https://hnrss.org/newest?points=150, https://lobste.rs/rss, https://www.producthunt.com/feed?category=artificial-intelligence, https://simonwillison.net/atom/everything/, https://huggingface.co/blog/feed.xml -> https://YuhiOtaniMAL.github.io/RSS-GPT/tech.xml
- https://www.cicnews.com/feed, https://api.io.canada.ca/io-server/gc/news/en/v2?dept=departmentofcitizenshipandimmigration&type=newsreleases&sort=publishedDate&orderBy=desc&pick=25&format=atom, https://www.google.com/alerts/feeds/17146422405023153028/2044183529610699947 -> https://YuhiOtaniMAL.github.io/RSS-GPT/immigration.xml
- https://www.google.co.jp/alerts/feeds/13978041598387954826/12912498221145568378, https://www.google.co.jp/alerts/feeds/13978041598387954826/17444517234348100381, https://www.google.co.jp/alerts/feeds/13978041598387954826/15167630761358206135, https://www.google.co.jp/alerts/feeds/13978041598387954826/16377391982950024117, https://www.google.co.jp/alerts/feeds/13978041598387954826/17318765439013393951, https://www.google.co.jp/alerts/feeds/13978041598387954826/18178695081020785052 -> https://YuhiOtaniMAL.github.io/RSS-GPT/j-address.xml
