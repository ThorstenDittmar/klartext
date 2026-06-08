import type { Meta, StoryObj } from "@storybook/react";
import { Breadcrumb } from ".";

const meta: Meta<typeof Breadcrumb> = {
  title: "Molecules/Breadcrumb",
  component: Breadcrumb,
  parameters: { layout: "padded" },
  tags: ["autodocs"],
};
export default meta;
type Story = StoryObj<typeof Breadcrumb>;

export const TwoLevels: Story = {
  args: {
    items: [
      { label: "Meine Werke", onClick: () => {} },
      { label: "Der Aufstand" },
    ],
  },
};

export const ThreeLevels: Story = {
  args: {
    items: [
      { label: "Meine Werke", onClick: () => {} },
      { label: "Der Aufstand", onClick: () => {} },
      { label: "Kapitel 1" },
    ],
  },
};

export const SlashSeparator: Story = {
  args: {
    items: [
      { label: "Meine Werke", onClick: () => {} },
      { label: "Der Aufstand" },
    ],
    separator: "slash",
  },
};

export const SingleLevel: Story = {
  args: {
    items: [{ label: "Der Aufstand" }],
  },
};
