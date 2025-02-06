class Phorganize < Formula
  include Language::Python::Virtualenv

  desc "Phorganize is a python script to organize photos and videos using embedded meta data in the files."
  homepage "https://github.com/rioriost/phorganize/"
  url "https://files.pythonhosted.org/packages/b3/75/842a3b1a4269b47a2ca68d4db07f08d725043e1166c65706fd973e157b45/phorganize-0.1.1.tar.gz"
  sha256 "d8f2674e1a0171d016a516ca64f4a381e74e11f121680506063a073768f8ef8e"
  license "MIT"

  depends_on "python@3.11"

  resource "python-magic" do
    url "https://files.pythonhosted.org/packages/da/db/0b3e28ac047452d079d375ec6798bf76a036a08182dbb39ed38116a49130/python-magic-0.4.27.tar.gz"
    sha256 "c1ba14b08e4a5f5c31a302b7721239695b2f0f058d125bd5ce1ee36b9d9d3c3b"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/phorganize", "--help"
  end
end
