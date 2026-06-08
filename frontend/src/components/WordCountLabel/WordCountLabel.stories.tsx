import type { Meta, StoryObj } from "@storybook/react";
import { WordCountLabel } from ".";

const meta: Meta<typeof WordCountLabel> = {
  title: "Atoms/WordCountLabel",
  component: WordCountLabel,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
};
export default meta;
type Story = StoryObj<typeof WordCountLabel>;

export const Default: Story = {
  args: { count: 0 },
};

export const Short: Story = {
  args: { count: 42 },
};

export const Long: Story = {
  args: { count: 1240 },
};

export const SmallSize: Story = {
  args: { count: 847, size: "sm" },
};
