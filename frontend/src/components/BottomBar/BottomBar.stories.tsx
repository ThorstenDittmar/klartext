import type { Meta, StoryObj } from "@storybook/react";
import { BottomBar } from ".";

const meta: Meta<typeof BottomBar> = {
  title: "Molecules/BottomBar",
  component: BottomBar,
  parameters: { layout: "fullscreen" },
  tags: ["autodocs"],
};
export default meta;
type Story = StoryObj<typeof BottomBar>;

export const Saved: Story = {
  args: { wordCount: 1240, saveStatus: "saved" },
};

export const Saving: Story = {
  args: { wordCount: 1240, saveStatus: "saving" },
};

export const Unsaved: Story = {
  args: { wordCount: 847, saveStatus: "unsaved" },
};

export const Empty: Story = {
  args: { wordCount: 0, saveStatus: "saved" },
};
