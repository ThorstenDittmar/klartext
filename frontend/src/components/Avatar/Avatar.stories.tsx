import type { Meta, StoryObj } from "@storybook/react";
import { Avatar } from ".";

const meta: Meta<typeof Avatar> = {
  title: "Atoms/Avatar",
  component: Avatar,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
  argTypes: {
    size: { control: "select", options: ["xs", "sm", "md", "lg"] },
  },
};
export default meta;

type Story = StoryObj<typeof Avatar>;

export const WithImage: Story = {
  args: { name: "Anna Bauer", imageUrl: "https://i.pravatar.cc/150?img=5", size: "md" },
};

export const Initials: Story = {
  args: { name: "Thomas Müller", size: "md" },
};

export const Placeholder: Story = {
  args: { size: "md" },
};

export const AllSizes: Story = {
  render: () => (
    <div style={{ display: "flex", gap: "16px", alignItems: "center" }}>
      <Avatar name="Anna Bauer" size="xs" />
      <Avatar name="Anna Bauer" size="sm" />
      <Avatar name="Anna Bauer" size="md" />
      <Avatar name="Anna Bauer" size="lg" />
    </div>
  ),
};

/** Colour is derived from the name — same name always gets the same colour. */
export const DeterministicColors: Story = {
  render: () => (
    <div style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
      {["Anna Bauer", "Thomas Müller", "Sophie Wagner", "Felix Schmidt", "Laura Klein"].map((name) => (
        <div key={name} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "6px" }}>
          <Avatar name={name} size="md" />
          <span style={{ fontSize: "11px", color: "var(--color-text-secondary)" }}>
            {name.split(" ").map(n => n[0]).join("")}
          </span>
        </div>
      ))}
    </div>
  ),
};
