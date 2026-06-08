import type { Meta, StoryObj } from "@storybook/react";
import { AutosaveIndicator } from ".";

const meta: Meta<typeof AutosaveIndicator> = {
  title: "Atoms/AutosaveIndicator",
  component: AutosaveIndicator,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
};
export default meta;
type Story = StoryObj<typeof AutosaveIndicator>;

export const Saved: Story = {
  args: { status: "saved" },
};

export const Saving: Story = {
  args: { status: "saving" },
};

export const Unsaved: Story = {
  args: { status: "unsaved" },
};
