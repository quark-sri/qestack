using Xunit; using FluentAssertions;
namespace Orders.Tests;

[Trait("Category", "feature-003")]
public class DiscountTests
{
    [Fact]
    [Trait("Category", "FR-001"), Trait("Category", "positive")]
    public void Applies_discount() { var r = Calc(100m); r.Should().Be(90m); }

    [Fact(Skip = "later")]
    [Trait("Category", "FR-001")]
    public void Skipped() { Assert.Equal(1, 1); }

    [Theory, InlineData(1), InlineData(2)]
    [Trait("Category", "FR-001")] [Trait("Category", "boundary")]
    public async Task Status_only(int x)
    {
        var resp = await _client.GetAsync($"/orders/{x}");
        resp.StatusCode.Should().Be(HttpStatusCode.OK);
    }

    [Fact] [Trait("Category", "FR-001")]
    public void Not_null() => Calc(1m).Should().NotBeNull();

    [Fact] [Trait("Category", "FR-001")]
    public void Hollow() { }

    [TestMethod] [TestCategory("FR-001")]
    public void MsTestStyle() { var s = @"verbatim ""{"" string"; Assert.AreEqual(2, Add(1,1)); }

    private static decimal Calc(decimal t) => t;
}
